"""Authentication router - login, register, OAuth"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from ..db import get_db
from ..models.user import User, UserRole, SubscriptionTier
from ..security.encryption import hash_password, verify_password
from ..security.jwt_handler import create_access_token, create_refresh_token, verify_token
from ..security.audit import log_action
from ..dependencies import get_current_user, get_client_info


router = APIRouter()


# Pydantic schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
    client_info: dict = Depends(get_client_info)
):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Strong password (min 8 characters)
    - **full_name**: User's full name
    - **phone_number**: Optional phone number
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        role=UserRole.AGENT,
        subscription_tier=SubscriptionTier.FREE_TRIAL,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate tokens
    token_data = {"user_id": new_user.id, "email": new_user.email, "role": new_user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"user_id": new_user.id})
    
    # Log action
    await log_action(
        db=db,
        action="user_register",
        user_id=new_user.id,
        description=f"New user registered: {new_user.email}",
        **client_info
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role.value,
            "subscription_tier": new_user.subscription_tier.value
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
    client_info: dict = Depends(get_client_info)
):
    """
    Login with email and password.
    
    - **email**: Registered email address
    - **password**: User password
    """
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        # Log failed attempt
        await log_action(
            db=db,
            action="login_failed",
            description=f"Failed login attempt: {credentials.email}",
            status="failure",
            **client_info
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Generate tokens
    token_data = {"user_id": user.id, "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"user_id": user.id})
    
    # Log successful login
    await log_action(
        db=db,
        action="login_success",
        user_id=user.id,
        description=f"User logged in: {user.email}",
        **client_info
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "subscription_tier": user.subscription_tier.value
        }
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    token_data = {"user_id": user.id, "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token({"user_id": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "subscription_tier": user.subscription_tier.value
        }
    )


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone_number": current_user.phone_number,
        "role": current_user.role.value,
        "subscription_tier": current_user.subscription_tier.value,
        "subscription_status": current_user.subscription_status,
        "is_verified": current_user.is_verified,
        "is_onboarded": current_user.is_onboarded,
        "ai_actions_used": current_user.ai_actions_this_month,
        "ai_actions_limit": current_user.ai_actions_limit,
        "created_at": current_user.created_at,
        "last_login_at": current_user.last_login_at
    }


# OAuth endpoints (Gmail, Outlook) - Placeholders
@router.get("/google/authorize")
async def google_oauth_authorize():
    """Initiate Google OAuth flow"""
    # Will implement with Google OAuth library
    return {"message": "Google OAuth authorization - to be implemented"}


@router.get("/google/callback")
async def google_oauth_callback():
    """Handle Google OAuth callback"""
    # Will implement with Google OAuth library
    return {"message": "Google OAuth callback - to be implemented"}


@router.get("/microsoft/authorize")
async def microsoft_oauth_authorize():
    """Initiate Microsoft OAuth flow"""
    # Will implement with Microsoft MSAL
    return {"message": "Microsoft OAuth authorization - to be implemented"}


@router.get("/microsoft/callback")
async def microsoft_oauth_callback():
    """Handle Microsoft OAuth callback"""
    # Will implement with Microsoft MSAL
    return {"message": "Microsoft OAuth callback - to be implemented"}

