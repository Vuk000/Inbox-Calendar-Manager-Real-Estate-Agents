"""Communication service for logging and managing all interactions"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
import logging

from ..models.communication_log import CommunicationLog, CommunicationType, CommunicationDirection
from ..models.contact import Contact
from ..models.user import User

logger = logging.getLogger(__name__)


class CommunicationService:
    """Service for managing communication logs across all channels"""
    
    @staticmethod
    async def log_communication(
        db: Session,
        user_id: int,
        contact_id: int,
        communication_type: CommunicationType,
        direction: CommunicationDirection,
        occurred_at: datetime,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        from_address: Optional[str] = None,
        to_address: Optional[str] = None,
        external_id: Optional[str] = None,
        property_id: Optional[int] = None,
        transaction_id: Optional[int] = None,
        sentiment_score: Optional[float] = None,
        urgency_score: Optional[float] = None,
        **kwargs
    ) -> CommunicationLog:
        """
        Log a communication with a contact
        
        Args:
            db: Database session
            user_id: User ID
            contact_id: Contact ID
            communication_type: Type of communication (EMAIL, SMS, etc.)
            direction: Direction (INBOUND, OUTBOUND, INTERNAL)
            occurred_at: When the communication occurred
            **kwargs: Additional fields
            
        Returns:
            Created CommunicationLog entry
        """
        try:
            comm_log = CommunicationLog(
                user_id=user_id,
                contact_id=contact_id,
                communication_type=communication_type,
                direction=direction,
                occurred_at=occurred_at,
                subject=subject,
                body=body,
                from_address=from_address,
                to_address=to_address,
                external_id=external_id,
                property_id=property_id,
                transaction_id=transaction_id,
                sentiment_score=sentiment_score,
                urgency_score=urgency_score,
                **kwargs
            )
            
            db.add(comm_log)
            db.commit()
            db.refresh(comm_log)
            
            # Update contact's last contact date and frequency
            contact = db.query(Contact).filter(Contact.id == contact_id).first()
            if contact:
                contact.last_contact_date = occurred_at
                contact.contact_frequency = (contact.contact_frequency or 0) + 1
                db.commit()
            
            return comm_log
            
        except Exception as e:
            logger.error(f"Error logging communication: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_contact_communications(
        db: Session,
        contact_id: int,
        user_id: int,
        communication_type: Optional[CommunicationType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[CommunicationLog]:
        """
        Get communications for a contact with optional filters
        
        Args:
            db: Database session
            contact_id: Contact ID
            user_id: User ID
            communication_type: Filter by type
            start_date: Filter from this date
            end_date: Filter to this date
            limit: Max results
            
        Returns:
            List of CommunicationLog entries
        """
        query = db.query(CommunicationLog).filter(
            CommunicationLog.contact_id == contact_id,
            CommunicationLog.user_id == user_id
        )
        
        if communication_type:
            query = query.filter(CommunicationLog.communication_type == communication_type)
        
        if start_date:
            query = query.filter(CommunicationLog.occurred_at >= start_date)
        
        if end_date:
            query = query.filter(CommunicationLog.occurred_at <= end_date)
        
        query = query.order_by(CommunicationLog.occurred_at.desc())
        
        return query.limit(limit).all()
    
    @staticmethod
    def get_communication_stats(
        db: Session,
        contact_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get communication statistics for a contact
        
        Args:
            db: Database session
            contact_id: Contact ID
            user_id: User ID
            
        Returns:
            Dict with statistics
        """
        comms = db.query(CommunicationLog).filter(
            CommunicationLog.contact_id == contact_id,
            CommunicationLog.user_id == user_id
        ).all()
        
        if not comms:
            return {
                "total_count": 0,
                "by_type": {},
                "by_direction": {},
                "avg_sentiment": None,
                "last_contact": None,
                "frequency_per_month": 0
            }
        
        # Count by type
        by_type = {}
        for comm in comms:
            comm_type = comm.communication_type.value
            by_type[comm_type] = by_type.get(comm_type, 0) + 1
        
        # Count by direction
        by_direction = {}
        for comm in comms:
            direction = comm.direction.value
            by_direction[direction] = by_direction.get(direction, 0) + 1
        
        # Average sentiment
        sentiments = [c.sentiment_score for c in comms if c.sentiment_score is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else None
        
        # Last contact
        last_contact = max(c.occurred_at for c in comms)
        
        # Frequency per month
        if len(comms) > 1:
            first_contact = min(c.occurred_at for c in comms)
            days_span = (last_contact - first_contact).days
            if days_span > 0:
                frequency_per_month = (len(comms) / days_span) * 30
            else:
                frequency_per_month = len(comms)
        else:
            frequency_per_month = 0
        
        return {
            "total_count": len(comms),
            "by_type": by_type,
            "by_direction": by_direction,
            "avg_sentiment": avg_sentiment,
            "last_contact": last_contact,
            "frequency_per_month": round(frequency_per_month, 2)
        }
    
    @staticmethod
    async def log_sms(
        db: Session,
        user_id: int,
        phone_number: str,
        direction: CommunicationDirection,
        body: str,
        occurred_at: datetime,
        external_id: Optional[str] = None
    ) -> Optional[CommunicationLog]:
        """
        Log an SMS and link to contact by phone number
        
        Args:
            db: Database session
            user_id: User ID
            phone_number: Phone number
            direction: INBOUND or OUTBOUND
            body: SMS body
            occurred_at: When it occurred
            external_id: Twilio message SID
            
        Returns:
            Created CommunicationLog or None
        """
        try:
            # Find contact by phone
            contact = db.query(Contact).filter(
                Contact.user_id == user_id,
                or_(
                    Contact.phone == phone_number,
                    Contact.secondary_phone == phone_number
                )
            ).first()
            
            if not contact:
                logger.warning(f"No contact found for phone {phone_number}")
                return None
            
            # Log communication
            comm_log = await CommunicationService.log_communication(
                db=db,
                user_id=user_id,
                contact_id=contact.id,
                communication_type=CommunicationType.SMS,
                direction=direction,
                occurred_at=occurred_at,
                body=body,
                from_address=phone_number if direction == CommunicationDirection.INBOUND else None,
                to_address=phone_number if direction == CommunicationDirection.OUTBOUND else None,
                external_id=external_id
            )
            
            return comm_log
            
        except Exception as e:
            logger.error(f"Error logging SMS: {str(e)}")
            return None

