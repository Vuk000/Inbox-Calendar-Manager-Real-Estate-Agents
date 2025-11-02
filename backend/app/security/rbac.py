"""Role-Based Access Control (RBAC)"""
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..models.user import User, SubscriptionTier, UserRole
from ..dependencies import get_db, get_current_user
from ..utils.subscription_utils import can_access_feature


# Role hierarchy and permissions
ROLE_PERMISSIONS = {
    UserRole.ADMIN: ["*"],  # Full access
    UserRole.AGENT: [
        "read:own_emails",
        "write:own_emails",
        "read:own_drafts",
        "write:own_drafts",
        "read:own_tasks",
        "write:own_tasks",
        "read:own_properties",
        "write:own_properties",
        "read:own_analytics",
        "manage:own_settings",
        "use:vision_scans",
        "use:neighborhood_searches",
    ],
    UserRole.TEAM_MEMBER: [
        "read:team_emails",
        "read:team_tasks",
        "write:own_tasks",
        "read:team_properties",
    ],
}


def check_permission(user_role: UserRole, required_permission: str) -> bool:
    """
    Check if user role has required permission.
    
    Args:
        user_role: User's role
        required_permission: Permission string (e.g., "read:emails")
        
    Returns:
        True if user has permission
    """
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    
    # Admin has all permissions
    if "*" in permissions:
        return True
    
    return required_permission in permissions


def require_role(allowed_roles: List[UserRole]):
    """
    Decorator to require specific roles for endpoint access.
    
    Args:
        allowed_roles: List of allowed user roles
        
    Usage:
        @require_role([UserRole.ADMIN, UserRole.AGENT])
        async def my_endpoint():
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would be used with FastAPI dependency injection
            # to get current user from request
            # For now, it's a placeholder
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_subscription_tier(
    required_tier: str = "pro",  # 'free', 'solo', 'pro', 'team'
    feature: Optional[str] = None
):
    """
    Dependency to require minimum subscription tier.
    
    Args:
        required_tier: Minimum tier required ('free', 'solo', 'pro', 'team')
        feature: Optional feature name for usage tracking
        
    Usage:
        @router.post("/premium-endpoint")
        async def premium_endpoint(
            current_user: User = Depends(require_subscription_tier("pro", "vision_scans"))
        ):
            pass
    """
    async def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        """Check subscription tier"""
        # Check tier requirement
        user_tier = current_user.get_simple_tier()
        tier_hierarchy = {'free': 1, 'solo': 2, 'pro': 3, 'team': 4}
        
        if tier_hierarchy.get(user_tier, 0) < tier_hierarchy.get(required_tier, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {required_tier} tier. Current tier: {user_tier}"
            )
        
        # Check usage limits if feature specified
        if feature:
            if not can_access_feature(db, current_user, feature, required_tier):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Usage limit reached for {feature}. Upgrade or wait for next billing cycle."
                )
        
        return current_user
    
    return dependency


def check_subscription_tier(user: User, required_tier: str) -> bool:
    """
    Check if user has required subscription tier.
    
    Args:
        user: User object
        required_tier: Required tier ('free', 'solo', 'pro', 'team')
        
    Returns:
        True if user meets tier requirement
    """
    user_tier = user.get_simple_tier()
    tier_hierarchy = {'free': 1, 'solo': 2, 'pro': 3, 'team': 4}
    
    return tier_hierarchy.get(user_tier, 0) >= tier_hierarchy.get(required_tier, 0)

