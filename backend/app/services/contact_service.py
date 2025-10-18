"""Contact service for CRM operations"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
import pandas as pd
import io
import logging

from ..models.contact import Contact
from ..models.communication_log import CommunicationLog
from ..shared.exceptions import ValidationException

logger = logging.getLogger(__name__)


class ContactService:
    """Service for contact management operations"""
    
    @staticmethod
    def create_contact(db: Session, user_id: int, contact_data: Dict[str, Any]) -> Contact:
        """Create a new contact"""
        contact = Contact(
            user_id=user_id,
            **contact_data
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact
    
    @staticmethod
    def get_contact(db: Session, contact_id: int, user_id: int) -> Optional[Contact]:
        """Get a single contact by ID"""
        return db.query(Contact).filter(
            Contact.id == contact_id,
            or_(
                Contact.user_id == user_id,
                Contact.is_shared_with_team == True
            )
        ).first()
    
    @staticmethod
    def list_contacts(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        contact_type: Optional[str] = None,
        contact_status: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Contact]:
        """List contacts with filters and pagination"""
        query = db.query(Contact).filter(
            or_(
                Contact.user_id == user_id,
                Contact.is_shared_with_team == True
            )
        )
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Contact.first_name.ilike(search_term),
                    Contact.last_name.ilike(search_term),
                    Contact.email.ilike(search_term),
                    Contact.phone.ilike(search_term),
                    Contact.company.ilike(search_term)
                )
            )
        
        # Apply type filter
        if contact_type:
            query = query.filter(Contact.contact_type == contact_type)
        
        # Apply status filter
        if contact_status:
            query = query.filter(Contact.contact_status == contact_status)
        
        # Apply tag filter
        if tags:
            for tag in tags:
                query = query.filter(Contact.tags.contains([tag]))
        
        # Order by relationship score (high to low)
        query = query.order_by(Contact.relationship_score.desc())
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_contact(
        db: Session,
        contact_id: int,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Contact]:
        """Update a contact"""
        contact = ContactService.get_contact(db, contact_id, user_id)
        if not contact:
            return None
        
        # Check if user owns the contact
        if contact.user_id != user_id:
            raise ValidationException("Cannot edit shared contact")
        
        for key, value in update_data.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        
        contact.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contact)
        return contact
    
    @staticmethod
    def delete_contact(db: Session, contact_id: int, user_id: int) -> bool:
        """Delete a contact"""
        contact = ContactService.get_contact(db, contact_id, user_id)
        if not contact:
            return False
        
        # Check if user owns the contact
        if contact.user_id != user_id:
            raise ValidationException("Cannot delete shared contact")
        
        db.delete(contact)
        db.commit()
        return True
    
    @staticmethod
    def share_contact_with_team(
        db: Session,
        contact_id: int,
        user_id: int,
        team_id: int
    ) -> Optional[Contact]:
        """Share contact with team"""
        contact = ContactService.get_contact(db, contact_id, user_id)
        if not contact:
            return None
        
        if contact.user_id != user_id:
            raise ValidationException("Cannot share contact you don't own")
        
        contact.is_shared_with_team = True
        contact.team_id = team_id
        contact.shared_by = user_id
        contact.shared_at = datetime.utcnow()
        
        db.commit()
        db.refresh(contact)
        return contact
    
    @staticmethod
    def import_from_csv(
        db: Session,
        user_id: int,
        csv_file: bytes,
        field_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Import contacts from CSV with field mapping"""
        try:
            # Read CSV file
            df = pd.read_csv(io.BytesIO(csv_file))
            
            # Validate required fields
            if 'first_name' not in field_mapping.values():
                raise ValidationException("first_name mapping is required")
            
            # Reverse mapping for easier lookup
            reverse_mapping = {v: k for k, v in field_mapping.items()}
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    contact_data = {}
                    
                    # Map CSV columns to contact fields
                    for db_field, csv_column in field_mapping.items():
                        if csv_column in df.columns and pd.notna(row[csv_column]):
                            contact_data[db_field] = str(row[csv_column]).strip()
                    
                    # Check for duplicates by email
                    if 'email' in contact_data:
                        existing = db.query(Contact).filter(
                            Contact.user_id == user_id,
                            Contact.email == contact_data['email']
                        ).first()
                        
                        if existing:
                            skipped_count += 1
                            continue
                    
                    # Create contact
                    contact = Contact(user_id=user_id, **contact_data)
                    db.add(contact)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
                    skipped_count += 1
            
            db.commit()
            
            return {
                "success": True,
                "imported_count": imported_count,
                "skipped_count": skipped_count,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"CSV import error: {str(e)}")
            raise ValidationException(f"Failed to import CSV: {str(e)}")
    
    @staticmethod
    def get_contact_timeline(
        db: Session,
        contact_id: int,
        user_id: int,
        limit: int = 50
    ) -> List[CommunicationLog]:
        """Get communication timeline for a contact"""
        contact = ContactService.get_contact(db, contact_id, user_id)
        if not contact:
            return []
        
        return db.query(CommunicationLog).filter(
            CommunicationLog.contact_id == contact_id
        ).order_by(
            CommunicationLog.occurred_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_or_create_contact_by_email(
        db: Session,
        email: str,
        user_id: int,
        sender_name: Optional[str] = None
    ) -> Contact:
        """
        Get existing contact by email or create a new one
        
        Args:
            db: Database session
            email: Email address
            user_id: User ID
            sender_name: Full name from email sender (optional)
            
        Returns:
            Contact object (existing or newly created)
        """
        # Try to find existing contact
        contact = db.query(Contact).filter(
            Contact.user_id == user_id,
            Contact.email == email
        ).first()
        
        if contact:
            return contact
        
        # Extract first and last name from sender_name
        first_name = "Unknown"
        last_name = None
        
        if sender_name:
            # Remove email address if present in name
            name_clean = sender_name.split('<')[0].strip().strip('"').strip("'")
            name_parts = name_clean.split()
            
            if len(name_parts) >= 1:
                first_name = name_parts[0]
            if len(name_parts) >= 2:
                last_name = ' '.join(name_parts[1:])
        
        # Create new contact
        contact = Contact(
            user_id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            contact_type="lead",
            contact_status="active",
            lead_source="email"
        )
        
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        logger.info(f"Auto-created contact {contact.id} for email {email}")
        return contact
    
    @staticmethod
    def get_or_create_contact_by_phone(
        db: Session,
        phone: str,
        user_id: int,
        name: Optional[str] = None
    ) -> Contact:
        """
        Get existing contact by phone or create a new one
        
        Args:
            db: Database session
            phone: Phone number
            user_id: User ID
            name: Contact name (optional)
            
        Returns:
            Contact object (existing or newly created)
        """
        # Try to find existing contact
        contact = db.query(Contact).filter(
            Contact.user_id == user_id,
            or_(
                Contact.phone == phone,
                Contact.secondary_phone == phone
            )
        ).first()
        
        if contact:
            return contact
        
        # Extract name
        first_name = "Unknown"
        last_name = None
        
        if name:
            name_parts = name.split()
            if len(name_parts) >= 1:
                first_name = name_parts[0]
            if len(name_parts) >= 2:
                last_name = ' '.join(name_parts[1:])
        
        # Create new contact
        contact = Contact(
            user_id=user_id,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            contact_type="lead",
            contact_status="active",
            lead_source="sms"
        )
        
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        logger.info(f"Auto-created contact {contact.id} for phone {phone}")
        return contact
    
    @staticmethod
    def merge_contacts(
        db: Session,
        primary_id: int,
        duplicate_id: int,
        user_id: int
    ) -> Optional[Contact]:
        """
        Merge duplicate contact into primary contact
        
        Args:
            db: Database session
            primary_id: Primary contact ID (keep this one)
            duplicate_id: Duplicate contact ID (will be deleted)
            user_id: User ID
            
        Returns:
            Updated primary contact or None if failed
        """
        try:
            # Get both contacts
            primary = ContactService.get_contact(db, primary_id, user_id)
            duplicate = ContactService.get_contact(db, duplicate_id, user_id)
            
            if not primary or not duplicate:
                logger.warning(f"Cannot merge: contacts not found")
                return None
            
            # Check ownership
            if primary.user_id != user_id or duplicate.user_id != user_id:
                raise ValidationException("Cannot merge contacts you don't own")
            
            # Merge data: fill in missing fields from duplicate
            if not primary.email and duplicate.email:
                primary.email = duplicate.email
            if not primary.phone and duplicate.phone:
                primary.phone = duplicate.phone
            if not primary.secondary_phone and duplicate.secondary_phone:
                primary.secondary_phone = duplicate.secondary_phone
            if not primary.company and duplicate.company:
                primary.company = duplicate.company
            if not primary.job_title and duplicate.job_title:
                primary.job_title = duplicate.job_title
            
            # Merge tags
            primary_tags = set(primary.tags or [])
            duplicate_tags = set(duplicate.tags or [])
            primary.tags = list(primary_tags.union(duplicate_tags))
            
            # Reassign all communications from duplicate to primary
            from ..models.communication_log import CommunicationLog
            db.query(CommunicationLog).filter(
                CommunicationLog.contact_id == duplicate_id
            ).update({CommunicationLog.contact_id: primary_id})
            
            # Reassign all transactions from duplicate to primary
            from ..models.transaction import Transaction
            db.query(Transaction).filter(
                Transaction.contact_id == duplicate_id
            ).update({Transaction.contact_id: primary_id})
            
            # Reassign all notes from duplicate to primary
            from ..models.note import Note
            db.query(Note).filter(
                Note.contact_id == duplicate_id
            ).update({Note.contact_id: primary_id})
            
            # Update relationship score and frequency
            primary.contact_frequency = (primary.contact_frequency or 0) + (duplicate.contact_frequency or 0)
            
            # Keep the more recent last contact date
            if duplicate.last_contact_date:
                if not primary.last_contact_date or duplicate.last_contact_date > primary.last_contact_date:
                    primary.last_contact_date = duplicate.last_contact_date
            
            # Delete duplicate
            db.delete(duplicate)
            db.commit()
            db.refresh(primary)
            
            logger.info(f"Merged contact {duplicate_id} into {primary_id}")
            return primary
            
        except Exception as e:
            logger.error(f"Error merging contacts: {str(e)}")
            db.rollback()
            raise ValidationException(f"Failed to merge contacts: {str(e)}")
    
    @staticmethod
    def detect_duplicates(
        db: Session,
        user_id: int,
        contact: Contact
    ) -> List[Contact]:
        """Detect potential duplicate contacts"""
        duplicates = []
        
        # Check by email
        if contact.email:
            email_matches = db.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.email == contact.email,
                Contact.id != contact.id
            ).all()
            duplicates.extend(email_matches)
        
        # Check by phone
        if contact.phone:
            phone_matches = db.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.phone == contact.phone,
                Contact.id != contact.id
            ).all()
            duplicates.extend(phone_matches)
        
        # Check by name similarity
        if contact.first_name and contact.last_name:
            name_matches = db.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.first_name == contact.first_name,
                Contact.last_name == contact.last_name,
                Contact.id != contact.id
            ).all()
            duplicates.extend(name_matches)
        
        # Remove duplicates from list
        return list(set(duplicates))

