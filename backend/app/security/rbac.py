"""Role-Based Access Control (RBAC)"""
from typing import List
from fastapi import HTTPException, status
from ..models.user import UserRole


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

