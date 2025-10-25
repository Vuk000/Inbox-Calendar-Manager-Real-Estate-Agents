"""
Integrations router - OAuth flows and external connections
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from ..dependencies import get_db
from ..models.user import User
from ..models.email_account import EmailAccount, EmailProvider
from ..models.social_account import SocialAccount, SocialProvider
from ..dependencies import get_current_user
from ..integrations.gmail_integration import GmailIntegration
from ..integrations.outlook_integration import OutlookIntegration
from ..integrations.twitter_integration import TwitterIntegration
from ..integrations.facebook_messenger import FacebookMessengerIntegration
from ..security.encryption import encrypt_data
from ..security.audit import log_action

router = APIRouter()


# Pydantic schemas
class EmailAccountResponse(BaseModel):
    id: int
    provider: str
    email_address: str
    is_active: bool
    is_primary: bool
    sync_status: str
    last_sync_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SocialAccountResponse(BaseModel):
    id: int
    provider: str
    handle: str
    display_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/integrations/email-accounts", response_model=list[EmailAccountResponse])
async def list_email_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all connected email accounts for current user"""
    accounts = db.query(EmailAccount).filter(
        EmailAccount.user_id == current_user.id
    ).all()
    
    return accounts


@router.get("/integrations/social-accounts", response_model=list[SocialAccountResponse])
async def list_social_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List connected social accounts."""
    accounts = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id
    ).all()
    return accounts


@router.get("/integrations/gmail/authorize")
async def gmail_authorize(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate Gmail OAuth flow.
    Redirects user to Google consent screen.
    """
    gmail = GmailIntegration()
    
    # Generate state token for CSRF protection (in production, store in Redis)
    state = f"user_{current_user.id}"
    
    auth_url = gmail.get_authorization_url(state=state)
    
    # Log action
    await log_action(
        db=db,
        action="gmail_auth_initiated",
        user_id=current_user.id,
        description="User initiated Gmail OAuth"
    )
    
    return {"auth_url": auth_url}


@router.get("/integrations/gmail/callback")
async def gmail_callback(
    code: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Handle Gmail OAuth callback.
    Exchanges code for tokens and stores encrypted.
    """
    # Extract user_id from state (in production, verify from Redis)
    if not state or not state.startswith("user_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    user_id = int(state.replace("user_", ""))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Exchange code for tokens
    gmail = GmailIntegration()
    try:
        tokens = gmail.exchange_code_for_tokens(code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange code: {str(e)}"
        )
    
    # Get user's email address from Google
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        creds = Credentials(token=tokens["access_token"])
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress', 'user@gmail.com')
    except Exception:
        email_address = "user@gmail.com"  # Fallback
    
    # Store encrypted tokens
    account = EmailAccount(
        user_id=user_id,
        provider=EmailProvider.GMAIL,
        email_address=email_address,
        encrypted_access_token=encrypt_data(tokens["access_token"]),
        encrypted_refresh_token=encrypt_data(tokens.get("refresh_token", "")),
        token_expires_at=datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600)),
        is_active=True,
        auto_sync_enabled=True
    )
    
    # Set as primary if it's the first account
    existing_count = db.query(EmailAccount).filter(
        EmailAccount.user_id == user_id
    ).count()
    account.is_primary = existing_count == 0
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    # Log action
    await log_action(
        db=db,
        action="gmail_connected",
        user_id=user_id,
        resource_type="email_account",
        resource_id=account.id,
        description=f"Connected Gmail account: {email_address}"
    )
    
    # Redirect to frontend success page
    return RedirectResponse(url="http://localhost:3000/settings?gmail_connected=true")


@router.get("/integrations/outlook/authorize")
async def outlook_authorize(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate Outlook OAuth flow.
    Redirects user to Microsoft consent screen.
    """
    outlook = OutlookIntegration()
    
    # Generate state token
    state = f"user_{current_user.id}"
    
    auth_url = outlook.get_authorization_url(state=state)
    
    # Log action
    await log_action(
        db=db,
        action="outlook_auth_initiated",
        user_id=current_user.id,
        description="User initiated Outlook OAuth"
    )
    
    return {"auth_url": auth_url}


@router.get("/integrations/outlook/callback")
async def outlook_callback(
    code: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle Outlook OAuth callback"""
    # Extract user_id from state
    if not state or not state.startswith("user_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    user_id = int(state.replace("user_", ""))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Exchange code for tokens
    outlook = OutlookIntegration()
    try:
        tokens = outlook.exchange_code_for_tokens(code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange code: {str(e)}"
        )
    
    # Get user's email address from Microsoft Graph
    try:
        import requests
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
        if response.status_code == 200:
            email_address = response.json().get('mail') or response.json().get('userPrincipalName', 'user@outlook.com')
        else:
            email_address = "user@outlook.com"
    except Exception:
        email_address = "user@outlook.com"  # Fallback
    
    # Store encrypted tokens
    account = EmailAccount(
        user_id=user_id,
        provider=EmailProvider.OUTLOOK,
        email_address=email_address,
        encrypted_access_token=encrypt_data(tokens["access_token"]),
        encrypted_refresh_token=encrypt_data(tokens.get("refresh_token", "")),
        token_expires_at=datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600)),
        is_active=True,
        auto_sync_enabled=True
    )
    
    # Set as primary if it's the first account
    existing_count = db.query(EmailAccount).filter(
        EmailAccount.user_id == user_id
    ).count()
    account.is_primary = existing_count == 0
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    # Log action
    await log_action(
        db=db,
        action="outlook_connected",
        user_id=user_id,
        resource_type="email_account",
        resource_id=account.id,
        description=f"Connected Outlook account: {email_address}"
    )
    
    # Redirect to frontend success page
    return RedirectResponse(url="http://localhost:3000/settings?outlook_connected=true")


@router.get("/integrations/twitter/authorize")
async def twitter_authorize(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redirect_uri: Optional[str] = Query(None)
):
    """Start Twitter OAuth."""
    twitter = TwitterIntegration()
    state = f"user_{current_user.id}"
    url = twitter.get_authorization_url(state=state)
    if redirect_uri:
        url += f"&redirect_uri={redirect_uri}"
    await log_action(
        db=db,
        action="twitter_auth_initiated",
        user_id=current_user.id,
        description="User initiated Twitter OAuth"
    )
    return {"auth_url": url}


@router.get("/integrations/twitter/callback")
async def twitter_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    if not state.startswith("user_"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter")
    user_id = int(state.replace("user_", ""))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    twitter = TwitterIntegration()
    tokens = twitter.exchange_code_for_tokens(code)
    encrypted = TwitterIntegration.encrypt_tokens(tokens)
    # Fetch profile for handle
    try:
        profile = twitter.get_authenticated_user(encrypted["encrypted_access_token"])
        handle = profile.get("data", {}).get("username", "twitter_user")
        display = profile.get("data", {}).get("name", handle)
    except Exception:
        handle = "twitter_user"
        display = None

    account = SocialAccount(
        user_id=user_id,
        provider=SocialProvider.TWITTER,
        handle=handle,
        display_name=display,
        encrypted_access_token=encrypted["encrypted_access_token"],
        encrypted_refresh_token=encrypted["encrypted_refresh_token"],
        token_expires_at=datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600)),
        is_active=True,
        auto_sync_enabled=True,
    )
    db.add(account)
    db.commit()
    await log_action(
        db=db,
        action="twitter_connected",
        user_id=user_id,
        resource_type="social_account",
        resource_id=account.id,
        description=f"Connected Twitter account @{handle}"
    )
    return RedirectResponse(url="http://localhost:3000/settings?twitter_connected=true")


@router.get("/integrations/facebook/authorize")
async def facebook_authorize(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    messenger = FacebookMessengerIntegration()
    state = f"user_{current_user.id}"
    url = messenger.get_authorization_url(state)
    await log_action(
        db=db,
        action="facebook_auth_initiated",
        user_id=current_user.id,
        description="User initiated Facebook OAuth"
    )
    return {"auth_url": url}


@router.get("/integrations/facebook/callback")
async def facebook_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    if not state.startswith("user_"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter")
    user_id = int(state.replace("user_", ""))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    messenger = FacebookMessengerIntegration()
    try:
        tokens = messenger.exchange_code_for_tokens(code)
        page = messenger.get_page_access_token(tokens.get("access_token"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Facebook OAuth failed: {exc}")

    encrypted = FacebookMessengerIntegration.encrypt_tokens(page.get("access_token"))
    account = SocialAccount(
        user_id=user_id,
        provider=SocialProvider.FACEBOOK_MESSENGER,
        handle=page.get("name", "facebook_page"),
        display_name=page.get("name"),
        encrypted_access_token=encrypted["encrypted_page_token"],
        encrypted_refresh_token=None,
        token_expires_at=None,
        page_id=page.get("id"),
        extra_metadata=str(page),
    )
    db.add(account)
    db.commit()
    await log_action(
        db=db,
        action="facebook_connected",
        user_id=user_id,
        resource_type="social_account",
        resource_id=account.id,
        description=f"Connected Facebook page {page.get('name')}"
    )
    return RedirectResponse(url="http://localhost:3000/settings?facebook_connected=true")


@router.delete("/integrations/social-accounts/{account_id}")
async def disconnect_social_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    account = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    await log_action(
        db=db,
        action="social_account_disconnected",
        user_id=current_user.id,
        resource_type="social_account",
        resource_id=account_id,
        description=f"Disconnected {account.provider.value} account {account.handle}"
    )
    db.delete(account)
    db.commit()
    return {"success": True, "account_id": account_id}


@router.delete("/integrations/email-accounts/{account_id}")
async def disconnect_email_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect and remove an email account"""
    account = db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # Log before deleting
    await log_action(
        db=db,
        action="email_account_disconnected",
        user_id=current_user.id,
        resource_type="email_account",
        resource_id=account_id,
        description=f"Disconnected {account.provider.value} account: {account.email_address}"
    )
    
    db.delete(account)
    db.commit()
    
    return {"success": True, "account_id": account_id}


@router.patch("/integrations/email-accounts/{account_id}/toggle")
async def toggle_email_account(
    account_id: int,
    enable: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable or disable email account sync"""
    account = db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    account.is_active = enable
    account.auto_sync_enabled = enable
    db.commit()
    
    return {"success": True, "account_id": account_id, "enabled": enable}


@router.post("/integrations/email-accounts/{account_id}/sync")
async def trigger_manual_sync(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger email sync for an account"""
    account = db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # Trigger sync based on provider
    from ..tasks.email_sync_task import sync_gmail_account, sync_outlook_account
    
    if account.provider == EmailProvider.GMAIL:
        task = sync_gmail_account.delay(current_user.id, account_id)
    else:
        task = sync_outlook_account.delay(current_user.id, account_id)
    
    return {
        "success": True,
        "message": "Sync initiated",
        "task_id": task.id
    }

