"""Authentication router - login, register, OAuth"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..dependencies import get_db
from ..models.user import User, UserRole, SubscriptionTier
from ..security.encryption import hash_password, verify_password
from ..security.jwt_handler import create_access_token, create_refresh_token, verify_token
from ..security.audit import log_action
from ..dependencies import get_current_user, get_client_info

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        429: {"description": "Too many requests"}
    }
)
limiter = Limiter(key_func=get_remote_address)


# Pydantic schemas
class UserRegister(BaseModel):
    """User registration request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=72, description="Password (8-72 characters)")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    phone_number: Optional[str] = Field(None, max_length=50, description="Optional phone number")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "agent@example.com",
                "password": "SecurePassword123!",
                "full_name": "John Doe",
                "phone_number": "+1-555-0123"
            }
        }


class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "agent@example.com",
                "password": "SecurePassword123!"
            }
        }


class UserInfo(BaseModel):
    """User information model"""
    id: int
    email: str
    full_name: Optional[str]
    phone_number: Optional[str]
    role: str
    subscription_tier: str
    subscription_status: Optional[str] = None
    is_verified: bool = False
    is_onboarded: bool = False
    ai_actions_used: int = 0
    ai_actions_limit: int = 500
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserInfo

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "agent@example.com",
                    "full_name": "John Doe",
                    "role": "agent",
                    "subscription_tier": "free_trial"
                }
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str = Field(..., description="Valid refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class ProfileUpdate(BaseModel):
    """Profile update request model"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated full name")
    phone_number: Optional[str] = Field(None, max_length=50, description="Updated phone number")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe Updated",
                "phone_number": "+1-555-0123"
            }
        }


class PasswordChange(BaseModel):
    """Password change request model"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=72, description="New password (8-72 characters)")

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewSecurePassword123!"
            }
        }


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="""
    Register a new user account.
    
    **Requirements:**
    - Email must be unique
    - Password must be at least 8 characters
    - Password will be truncated if over 72 bytes (bcrypt limit)
    
    **Returns:**
    - Access token (valid for 15 minutes)
    - Refresh token (valid for 30 days)
    - User information
    """,
    responses={
        201: {
            "description": "User registered successfully"
        },
        400: {
            "description": "Invalid input or email already registered",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Email already registered"
                    }
                }
            }
        }
    }
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserRegister,
    db: Session = Depends(get_db),
    client_info: dict = Depends(get_client_info)
):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Strong password (min 8 characters, max 72 bytes)
    - **full_name**: User's full name
    - **phone_number**: Optional phone number
    """
    # Optional password validation (informative)
    password_bytes = user_data.password.encode('utf-8')
    if len(password_bytes) > 72:
        # Password will be truncated - warn user but allow registration
        logger.warning(f"Password for {user_data.email} exceeds 72 bytes and will be truncated")
    
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
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
    token_data = {"sub": str(new_user.id), "email": new_user.email, "role": new_user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(new_user.id)})
    
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
        user=UserInfo(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            phone_number=new_user.phone_number,
            role=new_user.role.value,
            subscription_tier=new_user.subscription_tier.value,
            subscription_status=new_user.subscription_status,
            is_verified=new_user.is_verified,
            is_onboarded=new_user.is_onboarded,
            ai_actions_used=new_user.ai_actions_this_month,
            ai_actions_limit=new_user.ai_actions_limit,
            created_at=new_user.created_at,
            last_login_at=new_user.last_login_at
        )
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="""
    Authenticate user with email and password.
    
    **Security:**
    - Failed login attempts are logged
    - Inactive accounts are rejected
    - Returns JWT tokens for API access
    
    **Returns:**
    - Access token (valid for 15 minutes)
    - Refresh token (valid for 30 days)
    - User information
    """,
    responses={
        200: {
            "description": "Login successful"
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect email or password"
                    }
                }
            }
        },
        403: {
            "description": "Account inactive",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Account is inactive"
                    }
                }
            }
        }
    }
)
@limiter.limit("10/minute")
async def login(
    request: Request,
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
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
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
        user=UserInfo(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone_number=user.phone_number,
            role=user.role.value,
            subscription_tier=user.subscription_tier.value,
            subscription_status=user.subscription_status,
            is_verified=user.is_verified,
            is_onboarded=user.is_onboarded,
            ai_actions_used=user.ai_actions_this_month,
            ai_actions_limit=user.ai_actions_limit,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Access Token",
    description="""
    Refresh access token using a valid refresh token.
    
    **Security:**
    - Refresh token must be valid and not expired
    - User account must be active
    - Returns new access and refresh tokens
    """,
    responses={
        200: {
            "description": "Token refreshed successfully"
        },
        401: {
            "description": "Invalid or expired refresh token",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid or expired refresh token"
                    }
                }
            }
        }
    }
)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    # Verify refresh token
    payload = verify_token(refresh_request.refresh_token, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserInfo(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone_number=user.phone_number,
            role=user.role.value,
            subscription_tier=user.subscription_tier.value,
            subscription_status=user.subscription_status,
            is_verified=user.is_verified,
            is_onboarded=user.is_onboarded,
            ai_actions_used=user.ai_actions_this_month,
            ai_actions_limit=user.ai_actions_limit,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
    )


@router.get(
    "/me",
    response_model=UserInfo,
    summary="Get Current User",
    description="Get information about the currently authenticated user",
    responses={
        200: {
            "description": "User information retrieved successfully"
        },
        401: {
            "description": "Unauthorized - invalid or missing token"
        }
    }
)
@limiter.limit("30/minute")
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get information about the currently authenticated user"""
    return UserInfo(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        role=current_user.role.value,
        subscription_tier=current_user.subscription_tier.value,
        subscription_status=current_user.subscription_status,
        is_verified=current_user.is_verified,
        is_onboarded=current_user.is_onboarded,
        ai_actions_used=current_user.ai_actions_this_month,
        ai_actions_limit=current_user.ai_actions_limit,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )


@router.patch(
    "/me",
    response_model=UserInfo,
    summary="Update Profile",
    description="""
    Update user profile information.
    
    **Allowed Fields:**
    - full_name: User's full name
    - phone_number: User's phone number
    
    **Security:**
    - Requires authentication
    - All changes are logged for audit
    """,
    responses={
        200: {
            "description": "Profile updated successfully"
        },
        401: {
            "description": "Unauthorized"
        }
    }
)
@limiter.limit("10/minute")
async def update_profile(
    request: Request,
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    client_info: dict = Depends(get_client_info)
):
    """Update user profile information"""
    # Update fields
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    if profile_update.phone_number is not None:
        current_user.phone_number = profile_update.phone_number
    
    db.commit()
    db.refresh(current_user)
    
    # Log action
    await log_action(
        db=db,
        action="update_profile",
        user_id=current_user.id,
        description="User updated profile information",
        **client_info
    )
    
    return UserInfo(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        role=current_user.role.value,
        subscription_tier=current_user.subscription_tier.value,
        subscription_status=current_user.subscription_status,
        is_verified=current_user.is_verified,
        is_onboarded=current_user.is_onboarded,
        ai_actions_used=current_user.ai_actions_this_month,
        ai_actions_limit=current_user.ai_actions_limit,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change Password",
    description="""
    Change user password.
    
    **Requirements:**
    - Current password must be correct
    - New password must be at least 8 characters
    - Password will be truncated if over 72 bytes (bcrypt limit)
    
    **Security:**
    - Failed attempts are logged
    - Successful changes are logged for audit
    """,
    responses={
        200: {
            "description": "Password changed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Password changed successfully"
                    }
                }
            }
        },
        400: {
            "description": "Invalid current password or new password too short",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect current password"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized"
        }
    }
)
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    client_info: dict = Depends(get_client_info)
):
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        await log_action(
            db=db,
            action="change_password_failed",
            user_id=current_user.id,
            description="Failed password change - incorrect current password",
            status="failure",
            **client_info
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Validate new password length
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )
    
    # Informative check for password length (will be truncated if > 72 bytes)
    password_bytes = password_data.new_password.encode('utf-8')
    if len(password_bytes) > 72:
        logger.warning(f"Password for user {current_user.id} exceeds 72 bytes and will be truncated")
    
    # Update password
    current_user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    
    # Log action
    await log_action(
        db=db,
        action="change_password",
        user_id=current_user.id,
        description="User changed password",
        **client_info
    )
    
    return {"message": "Password changed successfully"}


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

