"""
Dependency injection providers for FastAPI
Provides reusable dependencies for routes
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from anthropic import Anthropic
import logging

from .db import SessionLocal
from .config import settings
from .agents.triage_agent import TriageAgent
from .agents.draft_agent import DraftAgent
from .agents.lead_qualification_agent import LeadQualificationAgent
from .integrations.gmail_integration import GmailIntegration
from .integrations.outlook_integration import OutlookIntegration
from .integrations.vector_store import VectorStore
from .security.jwt_handler import decode_access_token
from .models.user import User
from .shared.exceptions import AuthenticationException, InvalidTokenException

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


# Database
def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Yields a SQLAlchemy session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Authentication
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise InvalidTokenException("Token payload invalid")
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise AuthenticationException("User not found")
        
        if not user.is_active:
            raise AuthenticationException("User account is disabled")
        
        return user
        
    except (InvalidTokenException, AuthenticationException) as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify user is active.
    
    Args:
        current_user: Current user from token
        
    Returns:
        User: Active user
        
    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# AI Services - Claude Client
def get_claude_client() -> Anthropic:
    """
    Get Anthropic Claude client instance.
    
    Returns:
        Anthropic: Claude API client
    """
    return Anthropic(api_key=settings.ANTHROPIC_API_KEY)


# AI Agents with Dependency Injection
def get_triage_agent(
    claude_client: Anthropic = Depends(get_claude_client)
) -> TriageAgent:
    """
    Get TriageAgent instance with injected dependencies.
    
    Args:
        claude_client: Anthropic client
        
    Returns:
        TriageAgent: Configured triage agent
    """
    return TriageAgent(claude_client=claude_client)


def get_draft_agent(
    claude_client: Anthropic = Depends(get_claude_client)
) -> DraftAgent:
    """
    Get DraftAgent instance with injected dependencies.
    
    Args:
        claude_client: Anthropic client
        
    Returns:
        DraftAgent: Configured draft agent
    """
    return DraftAgent(claude_client=claude_client)


def get_lead_qualification_agent(
    claude_client: Anthropic = Depends(get_claude_client)
) -> LeadQualificationAgent:
    """
    Get LeadQualificationAgent instance with injected dependencies.
    
    Args:
        claude_client: Anthropic client
        
    Returns:
        LeadQualificationAgent: Configured lead qualification agent
    """
    return LeadQualificationAgent(claude_client=claude_client)


# Integrations
def get_gmail_integration() -> GmailIntegration:
    """
    Get Gmail integration instance.
    
    Returns:
        GmailIntegration: Gmail API integration
    """
    return GmailIntegration()


def get_outlook_integration() -> OutlookIntegration:
    """
    Get Outlook integration instance.
    
    Returns:
        OutlookIntegration: Outlook/Microsoft Graph integration
    """
    return OutlookIntegration()


def get_vector_store() -> VectorStore:
    """
    Get vector store instance.
    
    Returns:
        VectorStore: Pinecone vector store
    """
    return VectorStore()


# Authorization helpers
def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require admin role.
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Admin user
        
    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_agent_or_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require agent or admin role.
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Agent or admin user
        
    Raises:
        HTTPException: 403 if user is viewer
    """
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent or admin access required"
        )
    return current_user


# Rate limiting helper (to be used with slowapi)
def get_rate_limit_key(
    current_user: Optional[User] = Depends(get_current_user)
) -> str:
    """
    Get rate limit key for current user.
    
    Args:
        current_user: Current user (optional)
        
    Returns:
        str: Rate limit key (user_id or ip)
    """
    if current_user:
        return f"user:{current_user.id}"
    return "anonymous"


# Pagination helper
class PaginationParams:
    """
    Pagination parameters for list endpoints.
    """
    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100
    ):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)
        self.offset = (self.page - 1) * self.page_size
        
    @property
    def limit(self) -> int:
        return self.page_size


def get_pagination_params(
    page: int = 1,
    page_size: int = 20
) -> PaginationParams:
    """
    Get pagination parameters.
    
    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        PaginationParams: Pagination parameters
    """
    return PaginationParams(page=page, page_size=page_size)
