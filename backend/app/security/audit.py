"""Audit logging for compliance"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.audit_log import AuditLog


async def log_action(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    endpoint: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None
) -> AuditLog:
    """
    Log an action to the audit trail.
    
    Args:
        db: Database session
        action: Action name (e.g., "login", "read_email", "send_email")
        user_id: User performing action
        resource_type: Type of resource affected
        resource_id: ID of affected resource
        description: Human-readable description
        metadata: Additional context data
        ip_address: Client IP address
        user_agent: Client user agent
        endpoint: API endpoint called
        status: Action status (success, failure, error)
        error_message: Error details if failed
        
    Returns:
        Created AuditLog instance
    """
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        metadata=metadata,
        ip_address=ip_address,
        user_agent=user_agent,
        endpoint=endpoint,
        status=status,
        error_message=error_message,
        timestamp=datetime.utcnow()
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log

