"""Transaction service for deal pipeline management"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
import logging
import uuid

from ..models.transaction import Transaction, TransactionStage, TransactionType
from ..models.contact import Contact
from ..shared.exceptions import ValidationException

logger = logging.getLogger(__name__)


class TransactionService:
    """Service for transaction/deal management operations"""
    
    @staticmethod
    def create_transaction(
        db: Session,
        user_id: int,
        transaction_data: Dict[str, Any]
    ) -> Transaction:
        """Create a new transaction"""
        try:
            # Validate contact exists
            contact_id = transaction_data.get("contact_id")
            if contact_id:
                contact = db.query(Contact).filter(
                    Contact.id == contact_id,
                    or_(Contact.user_id == user_id, Contact.is_shared_with_team == True)
                ).first()
                
                if not contact:
                    raise ValidationException("Contact not found or access denied")
            
            # Generate public timeline UUID if transaction should be shareable
            if transaction_data.get("is_shared"):
                transaction_data["public_timeline_uuid"] = str(uuid.uuid4())
            
            transaction = Transaction(
                user_id=user_id,
                **transaction_data
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            logger.info(f"Created transaction {transaction.id} for user {user_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_transaction(
        db: Session,
        transaction_id: int,
        user_id: int
    ) -> Optional[Transaction]:
        """Get a single transaction by ID"""
        return db.query(Transaction).filter(
            Transaction.id == transaction_id,
            or_(
                Transaction.user_id == user_id,
                Transaction.is_shared == True
            )
        ).first()
    
    @staticmethod
    def list_transactions(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        stage: Optional[TransactionStage] = None,
        transaction_type: Optional[TransactionType] = None,
        contact_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[Transaction]:
        """List transactions with filters and pagination"""
        query = db.query(Transaction).filter(
            or_(
                Transaction.user_id == user_id,
                Transaction.is_shared == True
            )
        )
        
        # Apply stage filter
        if stage:
            query = query.filter(Transaction.stage == stage)
        
        # Apply type filter
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        
        # Apply contact filter
        if contact_id:
            query = query.filter(Transaction.contact_id == contact_id)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Transaction.title.ilike(search_term),
                    Transaction.description.ilike(search_term)
                )
            )
        
        # Order by pipeline position and creation date
        query = query.order_by(
            Transaction.pipeline_position.asc(),
            Transaction.created_at.desc()
        )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_transaction(
        db: Session,
        transaction_id: int,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Transaction]:
        """Update a transaction"""
        transaction = TransactionService.get_transaction(db, transaction_id, user_id)
        if not transaction:
            return None
        
        # Check if user owns the transaction
        if transaction.user_id != user_id:
            raise ValidationException("Cannot edit shared transaction")
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(transaction, key) and key not in ['id', 'user_id', 'created_at']:
                setattr(transaction, key, value)
        
        # Auto-update closed_at when stage changes to CLOSED_WON or CLOSED_LOST
        if 'stage' in update_data:
            new_stage = update_data['stage']
            if new_stage in [TransactionStage.CLOSED_WON, TransactionStage.CLOSED_LOST]:
                if not transaction.closed_at:
                    transaction.closed_at = datetime.utcnow()
        
        transaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Updated transaction {transaction_id}")
        return transaction
    
    @staticmethod
    def delete_transaction(
        db: Session,
        transaction_id: int,
        user_id: int
    ) -> bool:
        """Delete a transaction"""
        transaction = TransactionService.get_transaction(db, transaction_id, user_id)
        if not transaction:
            return False
        
        # Check if user owns the transaction
        if transaction.user_id != user_id:
            raise ValidationException("Cannot delete shared transaction")
        
        db.delete(transaction)
        db.commit()
        
        logger.info(f"Deleted transaction {transaction_id}")
        return True
    
    @staticmethod
    def update_stage(
        db: Session,
        transaction_id: int,
        user_id: int,
        new_stage: TransactionStage,
        outcome_reason: Optional[str] = None
    ) -> Optional[Transaction]:
        """Update transaction stage (move through pipeline)"""
        transaction = TransactionService.get_transaction(db, transaction_id, user_id)
        if not transaction:
            return None
        
        if transaction.user_id != user_id:
            raise ValidationException("Cannot modify shared transaction")
        
        old_stage = transaction.stage
        transaction.stage = new_stage
        
        # Update stage-specific dates
        if new_stage == TransactionStage.UNDER_CONTRACT and not transaction.contract_date:
            transaction.contract_date = datetime.utcnow()
        
        if new_stage in [TransactionStage.CLOSED_WON, TransactionStage.CLOSED_LOST]:
            if not transaction.closed_at:
                transaction.closed_at = datetime.utcnow()
            
            if outcome_reason:
                transaction.outcome_reason = outcome_reason
        
        # Add timeline event
        timeline_events = transaction.timeline_events or []
        timeline_events.append({
            "date": datetime.utcnow().isoformat(),
            "title": f"Stage changed: {old_stage.value} → {new_stage.value}",
            "description": outcome_reason if outcome_reason else f"Transaction moved to {new_stage.value}",
            "type": "stage_change"
        })
        transaction.timeline_events = timeline_events
        
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Transaction {transaction_id} stage: {old_stage} → {new_stage}")
        return transaction
    
    @staticmethod
    def get_transaction_timeline(
        db: Session,
        transaction_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Get timeline for a transaction (events + communications)"""
        transaction = TransactionService.get_transaction(db, transaction_id, user_id)
        if not transaction:
            return {"events": [], "communications": []}
        
        # Get communication logs related to this transaction
        from ..models.communication_log import CommunicationLog
        
        communications = db.query(CommunicationLog).filter(
            CommunicationLog.transaction_id == transaction_id
        ).order_by(
            CommunicationLog.occurred_at.desc()
        ).limit(50).all()
        
        return {
            "timeline_events": transaction.timeline_events or [],
            "communications": communications,
            "checklist_items": transaction.checklist_items or []
        }
    
    @staticmethod
    def update_checklist(
        db: Session,
        transaction_id: int,
        user_id: int,
        checklist_items: List[Dict[str, Any]]
    ) -> Optional[Transaction]:
        """Update transaction checklist items"""
        transaction = TransactionService.get_transaction(db, transaction_id, user_id)
        if not transaction:
            return None
        
        if transaction.user_id != user_id:
            raise ValidationException("Cannot modify shared transaction")
        
        transaction.checklist_items = checklist_items
        transaction.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transaction)
        
        return transaction
    
    @staticmethod
    def get_pipeline_stats(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """Get pipeline statistics (count by stage, total value, etc.)"""
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.stage.notin_([TransactionStage.CLOSED_LOST, TransactionStage.ARCHIVED])
        ).all()
        
        # Count by stage
        by_stage = {}
        for stage in TransactionStage:
            by_stage[stage.value] = 0
        
        total_estimated_value = 0
        total_estimated_commission = 0
        
        for txn in transactions:
            by_stage[txn.stage.value] += 1
            if txn.estimated_value:
                total_estimated_value += txn.estimated_value
            if txn.estimated_commission:
                total_estimated_commission += txn.estimated_commission
        
        return {
            "total_active": len(transactions),
            "by_stage": by_stage,
            "total_estimated_value": total_estimated_value,
            "total_estimated_commission": total_estimated_commission
        }

