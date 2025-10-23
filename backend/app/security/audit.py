"""
Audit logging for compliance and security
Enhanced with SQLAlchemy event listeners for automatic CRUD tracking
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import event
from datetime import datetime
import logging

from ..models.audit_log import AuditLog

logger = logging.getLogger(__name__)


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


def setup_audit_listeners():
    """
    Setup SQLAlchemy event listeners for automatic audit logging.
    Call this during application startup to enable audit tracking.
    """
    from ..models.communication_log import CommunicationLog
    from ..models.draft import Draft
    from ..models.task import Task
    from ..models.user import User as UserModel
    
    # Track CommunicationLog updates (for important communications)
    @event.listens_for(CommunicationLog, 'after_update')
    def log_communication_update(mapper, connection, target):
        """Log communication updates"""
        # Note: This runs in the same transaction
        try:
            changes = {}
            state = target.__dict__
            if state.get('_sa_instance_state'):
                history = state['_sa_instance_state'].history
                for attr in history:
                    if history[attr].has_changes():
                        changes[attr] = {
                            'old': history[attr].deleted,
                            'new': history[attr].added
                        }
            
            if changes:
                # Insert audit log directly via connection
                connection.execute(
                    AuditLog.__table__.insert().values(
                        user_id=target.user_id,
                        action='update_communication',
                        resource_type='communication_log',
                        resource_id=target.id,
                        description=f'Updated communication: {(target.subject or "")[:50]}',
                        metadata={'changes': str(changes)},
                        timestamp=datetime.utcnow(),
                        status='success'
                    )
                )
        except Exception as e:
            logger.error(f"Failed to log communication update: {str(e)}")
    
    # Track Draft operations
    @event.listens_for(Draft, 'after_insert')
    def log_draft_create(mapper, connection, target):
        """Log draft creation"""
        try:
            connection.execute(
                AuditLog.__table__.insert().values(
                    user_id=getattr(target, 'user_id', None),
                    action='create_draft',
                    resource_type='draft',
                    resource_id=target.id,
                    description=f'Generated draft for email {target.email_id}',
                    metadata={'email_id': target.email_id},
                    timestamp=datetime.utcnow(),
                    status='success'
                )
            )
        except Exception as e:
            logger.error(f"Failed to log draft creation: {str(e)}")
    
    @event.listens_for(Draft, 'after_update')
    def log_draft_update(mapper, connection, target):
        """Log draft approvals/rejections"""
        try:
            connection.execute(
                AuditLog.__table__.insert().values(
                    user_id=getattr(target, 'user_id', None),
                    action='update_draft',
                    resource_type='draft',
                    resource_id=target.id,
                    description=f'Draft status changed to: {target.status}',
                    metadata={'status': target.status, 'email_id': target.email_id},
                    timestamp=datetime.utcnow(),
                    status='success'
                )
            )
        except Exception as e:
            logger.error(f"Failed to log draft update: {str(e)}")
    
    # Track Task operations
    @event.listens_for(Task, 'after_insert')
    def log_task_create(mapper, connection, target):
        """Log task creation"""
        try:
            connection.execute(
                AuditLog.__table__.insert().values(
                    user_id=target.created_by,
                    action='create_task',
                    resource_type='task',
                    resource_id=target.id,
                    description=f'Created task: {target.title[:50]}',
                    metadata={'priority': target.priority, 'status': target.status},
                    timestamp=datetime.utcnow(),
                    status='success'
                )
            )
        except Exception as e:
            logger.error(f"Failed to log task creation: {str(e)}")
    
    @event.listens_for(Task, 'after_update')
    def log_task_update(mapper, connection, target):
        """Log task status changes"""
        try:
            connection.execute(
                AuditLog.__table__.insert().values(
                    user_id=getattr(target, 'updated_by', target.created_by),
                    action='update_task',
                    resource_type='task',
                    resource_id=target.id,
                    description=f'Task updated: {target.title[:50]}',
                    metadata={'status': target.status, 'priority': target.priority},
                    timestamp=datetime.utcnow(),
                    status='success'
                )
            )
        except Exception as e:
            logger.error(f"Failed to log task update: {str(e)}")
    
    # Track sensitive User operations
    @event.listens_for(UserModel, 'after_update')
    def log_user_update(mapper, connection, target):
        """Log user profile/settings changes"""
        try:
            connection.execute(
                AuditLog.__table__.insert().values(
                    user_id=target.id,
                    action='update_profile',
                    resource_type='user',
                    resource_id=target.id,
                    description=f'User profile updated: {target.email}',
                    metadata={'is_active': target.is_active, 'role': target.role},
                    timestamp=datetime.utcnow(),
                    status='success'
                )
            )
        except Exception as e:
            logger.error(f"Failed to log user update: {str(e)}")
    
    logger.info("✅ Audit event listeners registered")

