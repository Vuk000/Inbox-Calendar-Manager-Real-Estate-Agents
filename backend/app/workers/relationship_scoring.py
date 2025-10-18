"""
Relationship scoring background workers using Celery
Handles periodic calculation of contact relationship scores
"""
from typing import Dict, Any
from celery import Task
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from .celery_app import celery_app
from ..db import SessionLocal
from ..models.contact import Contact
from ..services.relationship_service import RelationshipService
from ..security.audit import log_action

logger = logging.getLogger(__name__)


class BaseRelationshipTask(Task):
    """Base task with database session management"""
    
    def __call__(self, *args, **kwargs):
        db = SessionLocal()
        try:
            return self.run(*args, db=db, **kwargs)
        finally:
            db.close()


@celery_app.task(base=BaseRelationshipTask, bind=True)
def update_contact_relationship_score(self, contact_id: int, user_id: int, db: Session = None):
    """
    Update relationship score for a single contact
    
    Args:
        contact_id: Contact ID
        user_id: User ID
        db: Database session
    """
    try:
        service = RelationshipService()
        
        # Import asyncio here to avoid issues
        import asyncio
        
        # Update score
        contact = asyncio.run(service.update_contact_score(
            db=db,
            contact_id=contact_id,
            user_id=user_id
        ))
        
        if contact:
            logger.info(f"Updated relationship score for contact {contact_id}: {contact.relationship_score}")
            return {
                "status": "success",
                "contact_id": contact_id,
                "relationship_score": contact.relationship_score
            }
        else:
            logger.warning(f"Contact {contact_id} not found for scoring")
            return {
                "status": "not_found",
                "contact_id": contact_id
            }
            
    except Exception as e:
        logger.exception(f"Error updating relationship score for contact {contact_id}")
        return {
            "status": "error",
            "contact_id": contact_id,
            "error": str(e)
        }


@celery_app.task(base=BaseRelationshipTask, bind=True)
def bulk_update_relationship_scores(self, user_id: int, limit: int = 50, db: Session = None):
    """
    Update relationship scores for multiple contacts (batch job)
    
    Args:
        user_id: User ID
        limit: Maximum number of contacts to update
        db: Database session
    """
    try:
        service = RelationshipService()
        
        import asyncio
        
        # Run bulk update
        result = asyncio.run(service.bulk_update_scores(
            db=db,
            user_id=user_id,
            limit=limit
        ))
        
        # Log audit
        asyncio.run(log_action(
            db=db,
            action="bulk_relationship_score_update",
            user_id=user_id,
            description=f"Updated relationship scores for {result['updated_count']} contacts",
            metadata=result
        ))
        
        logger.info(f"Bulk update complete for user {user_id}: {result}")
        
        return result
        
    except Exception as e:
        logger.exception(f"Error in bulk relationship score update for user {user_id}")
        return {
            "status": "error",
            "error": str(e),
            "updated_count": 0,
            "failed_count": 0
        }


@celery_app.task(base=BaseRelationshipTask)
def update_all_active_contacts(db: Session = None):
    """
    Update relationship scores for all users' active contacts (periodic task)
    
    This should be scheduled to run daily.
    """
    from ..models.user import User
    
    try:
        # Get all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        queued_count = 0
        
        for user in users:
            # Queue bulk update for each user
            bulk_update_relationship_scores.delay(user.id, limit=100)
            queued_count += 1
        
        logger.info(f"Queued relationship score updates for {queued_count} users")
        
        return {
            "status": "queued",
            "users_count": queued_count
        }
        
    except Exception as e:
        logger.exception("Error queuing relationship score updates")
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task(base=BaseRelationshipTask)
def update_scores_for_recent_communications(db: Session = None):
    """
    Update relationship scores for contacts with recent communications
    
    This should be scheduled to run every few hours.
    """
    from ..models.communication_log import CommunicationLog
    from datetime import timedelta
    
    try:
        # Get contacts with communications in the last 24 hours
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        
        recent_comm_logs = db.query(CommunicationLog).filter(
            CommunicationLog.occurred_at >= recent_cutoff
        ).distinct(CommunicationLog.contact_id, CommunicationLog.user_id).all()
        
        queued_count = 0
        
        for comm_log in recent_comm_logs:
            # Queue individual update
            update_contact_relationship_score.delay(
                contact_id=comm_log.contact_id,
                user_id=comm_log.user_id
            )
            queued_count += 1
        
        logger.info(f"Queued {queued_count} contact score updates based on recent activity")
        
        return {
            "status": "queued",
            "contacts_count": queued_count
        }
        
    except Exception as e:
        logger.exception("Error queuing recent activity score updates")
        return {
            "status": "error",
            "error": str(e)
        }

