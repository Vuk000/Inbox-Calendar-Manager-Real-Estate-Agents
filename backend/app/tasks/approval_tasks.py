"""Celery tasks for human-in-loop approval queues"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..workers.celery_app import celery_app
from ..models.approval_queue import ApprovalQueue, ApprovalFeatureType, ApprovalStatus
from ..db import SessionLocal
from ..utils.cache import redis_client

logger = logging.getLogger(__name__)

# Only import Task if celery_app is available
if celery_app is not None:
    from celery import Task
else:
    # Mock Task class if Celery unavailable
    class Task:
        pass


# Decorator helper for conditional Celery task registration
def celery_task(*args, **kwargs):
    """Conditional Celery task decorator - only registers if celery_app is available"""
    if celery_app is not None:
        return celery_app.task(*args, **kwargs)
    else:
        # Return a no-op decorator if Celery unavailable
        def decorator(func):
            logger.warning(f"Celery unavailable - task {func.__name__} will not be registered")
            return func
        return decorator


@celery_task(name="approval.queue_item")
def queue_for_approval(
    user_id: int,
    feature_type: str,
    feature_id: Optional[int],
    data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    expires_hours: int = 24
) -> Dict[str, Any]:
    """
    Queue an item for human approval.
    
    Args:
        user_id: User ID
        feature_type: Feature type (vision_scan, neighborhood_report, etc.)
        feature_id: Optional feature ID
        data: Data requiring approval
        context: Optional context
        expires_hours: Hours until expiration
        
    Returns:
        Approval queue item ID
    """
    db = SessionLocal()
    try:
        approval_item = ApprovalQueue(
            user_id=user_id,
            feature_type=ApprovalFeatureType(feature_type),
            feature_id=feature_id,
            data=data,
            context=context or {},
            status=ApprovalStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours)
        )
        
        db.add(approval_item)
        db.commit()
        db.refresh(approval_item)
        
        # Store in Redis for quick access
        if redis_client:
            redis_key = f"approval:{approval_item.id}"
            redis_client.setex(
                redis_key,
                3600 * expires_hours,
                str(approval_item.id)
            )
        
        logger.info(f"Queued approval item {approval_item.id} for user {user_id}")
        
        return {
            "success": True,
            "approval_id": approval_item.id,
            "status": "pending"
        }
        
    finally:
        db.close()


@celery_task(name="approval.process_expired")
def process_expired_approvals():
    """Process expired approval queue items"""
    db = SessionLocal()
    try:
        expired_items = db.query(ApprovalQueue).filter(
            ApprovalQueue.status == ApprovalStatus.PENDING,
            ApprovalQueue.expires_at < datetime.utcnow()
        ).all()
        
        for item in expired_items:
            item.status = ApprovalStatus.EXPIRED
            db.commit()
            logger.info(f"Expired approval item {item.id}")
        
        return {
            "success": True,
            "expired_count": len(expired_items)
        }
        
    finally:
        db.close()


@celery_task(name="approval.send_notification")
def send_approval_notification(approval_id: int):
    """
    Send notification for approval request.
    
    Args:
        approval_id: Approval queue item ID
    """
    db = SessionLocal()
    try:
        item = db.query(ApprovalQueue).filter(ApprovalQueue.id == approval_id).first()
        if not item:
            return {"success": False, "error": "Item not found"}
        
        # In production, send WebSocket notification or email
        # For now, just log
        logger.info(f"Approval notification: Item {approval_id} for user {item.user_id}")
        
        return {"success": True}
        
    finally:
        db.close()

