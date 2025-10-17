"""Relationship service for managing contact relationship scores"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from ..models.contact import Contact
from ..models.communication_log import CommunicationLog
from ..models.transaction import Transaction
from ..agents.relationship_agent import RelationshipAgent

logger = logging.getLogger(__name__)


class RelationshipService:
    """Service for calculating and updating relationship scores"""
    
    def __init__(self):
        self.agent = RelationshipAgent()
    
    async def update_contact_score(
        self,
        db: Session,
        contact_id: int,
        user_id: int
    ) -> Optional[Contact]:
        """
        Calculate and update relationship score for a contact
        
        Args:
            db: Database session
            contact_id: Contact ID
            user_id: User ID (for permission check)
            
        Returns:
            Updated Contact object or None if not found
        """
        try:
            # Get contact
            contact = db.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == user_id
            ).first()
            
            if not contact:
                return None
            
            # Get communications
            communications = db.query(CommunicationLog).filter(
                CommunicationLog.contact_id == contact_id
            ).order_by(
                CommunicationLog.occurred_at.desc()
            ).limit(50).all()
            
            # Get transactions
            transactions = db.query(Transaction).filter(
                Transaction.contact_id == contact_id
            ).all()
            
            # Convert to dicts for agent
            contact_dict = {
                "id": contact.id,
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "email": contact.email,
                "phone": contact.phone,
                "contact_type": contact.contact_type,
                "contact_status": contact.contact_status
            }
            
            comm_dict = [{
                "id": c.id,
                "communication_type": c.communication_type.value if c.communication_type else None,
                "direction": c.direction.value if c.direction else None,
                "occurred_at": c.occurred_at,
                "subject": c.subject,
                "summary": c.summary,
                "sentiment_score": c.sentiment_score
            } for c in communications]
            
            trans_dict = [{
                "id": t.id,
                "stage": t.stage.value if t.stage else None,
                "transaction_type": t.transaction_type.value if t.transaction_type else None,
                "estimated_value": t.estimated_value
            } for t in transactions]
            
            # Calculate score
            result = await self.agent.calculate_relationship_score(
                contact=contact_dict,
                communications=comm_dict,
                transactions=trans_dict
            )
            
            # Update contact
            contact.relationship_score = result["relationship_score"]
            contact.ai_insights = {
                "insights": result.get("insights", []),
                "communication_pattern": result.get("communication_pattern", ""),
                "sentiment_trend": result.get("sentiment_trend", ""),
                "suggested_actions": result.get("suggested_actions", []),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Update last contact date
            if communications:
                contact.last_contact_date = communications[0].occurred_at
            
            contact.contact_frequency = len(communications)
            contact.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(contact)
            
            return contact
            
        except Exception as e:
            logger.error(f"Error updating contact score: {str(e)}")
            db.rollback()
            return None
    
    async def bulk_update_scores(
        self,
        db: Session,
        user_id: int,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Update relationship scores for multiple contacts (background task)
        
        Args:
            db: Database session
            user_id: User ID
            limit: Max number of contacts to update
            
        Returns:
            Dict with update statistics
        """
        try:
            # Get contacts that need score updates
            # Prioritize contacts with recent activity or no score
            contacts = db.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.contact_status == "active"
            ).order_by(
                Contact.last_contact_date.desc().nullsfirst()
            ).limit(limit).all()
            
            updated_count = 0
            failed_count = 0
            
            for contact in contacts:
                result = await self.update_contact_score(db, contact.id, user_id)
                if result:
                    updated_count += 1
                else:
                    failed_count += 1
            
            return {
                "success": True,
                "updated_count": updated_count,
                "failed_count": failed_count,
                "total_processed": len(contacts)
            }
            
        except Exception as e:
            logger.error(f"Bulk score update error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "updated_count": 0,
                "failed_count": 0,
                "total_processed": 0
            }
    
    def get_score_history(
        self,
        db: Session,
        contact_id: int,
        user_id: int
    ) -> list:
        """
        Get historical relationship scores for a contact
        (Placeholder - would need a separate score_history table)
        
        Args:
            db: Database session
            contact_id: Contact ID
            user_id: User ID
            
        Returns:
            List of score history entries
        """
        # TODO: Implement score history tracking
        # For now, return current score only
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.user_id == user_id
        ).first()
        
        if not contact:
            return []
        
        return [{
            "date": contact.updated_at or contact.created_at,
            "score": contact.relationship_score,
            "insights": contact.ai_insights
        }]

