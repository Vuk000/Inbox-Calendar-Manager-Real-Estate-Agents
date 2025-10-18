"""
Tests for Contact Service
Ensures robust contact management operations
"""
import pytest
from sqlalchemy.orm import Session
from app.services.contact_service import ContactService
from app.models.contact import Contact
from app.models.communication_log import CommunicationLog, CommunicationType, CommunicationDirection
from app.models.user import User
from app.shared.exceptions import ValidationException


@pytest.fixture
def test_user(db: Session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_contact(db: Session, test_user: User):
    """Create a test contact"""
    contact = Contact(
        user_id=test_user.id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="555-1234"
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


class TestGetOrCreateContactByEmail:
    """Test get_or_create_contact_by_email functionality"""
    
    def test_creates_new_contact_when_not_exists(self, db: Session, test_user: User):
        """Should create a new contact if email doesn't exist"""
        email = "newuser@example.com"
        sender_name = "Jane Smith"
        
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email=email,
            user_id=test_user.id,
            sender_name=sender_name
        )
        
        assert contact.id is not None
        assert contact.email == email
        assert contact.first_name == "Jane"
        assert contact.last_name == "Smith"
        assert contact.user_id == test_user.id
        assert contact.contact_type == "lead"
        assert contact.lead_source == "email"
    
    def test_returns_existing_contact_when_exists(self, db: Session, test_user: User, test_contact: Contact):
        """Should return existing contact if email already exists"""
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email=test_contact.email,
            user_id=test_user.id,
            sender_name="Different Name"
        )
        
        assert contact.id == test_contact.id
        assert contact.email == test_contact.email
        # Original name should be preserved
        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
    
    def test_handles_single_name(self, db: Session, test_user: User):
        """Should handle sender with only first name"""
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="single@example.com",
            user_id=test_user.id,
            sender_name="Madonna"
        )
        
        assert contact.first_name == "Madonna"
        assert contact.last_name is None
    
    def test_parses_email_in_name(self, db: Session, test_user: User):
        """Should parse name from 'Name <email>' format"""
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="test@example.com",
            user_id=test_user.id,
            sender_name='"Bob Jones" <bob@example.com>'
        )
        
        assert contact.first_name == "Bob"
        assert contact.last_name == "Jones"
    
    def test_handles_no_sender_name(self, db: Session, test_user: User):
        """Should create contact with Unknown name if no sender_name"""
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="unknown@example.com",
            user_id=test_user.id,
            sender_name=None
        )
        
        assert contact.first_name == "Unknown"
        assert contact.last_name is None


class TestMergeContacts:
    """Test merge_contacts functionality"""
    
    def test_merges_contact_data(self, db: Session, test_user: User):
        """Should merge data from duplicate into primary contact"""
        # Create primary contact (sparse data)
        primary = Contact(
            user_id=test_user.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db.add(primary)
        
        # Create duplicate contact (more complete data)
        duplicate = Contact(
            user_id=test_user.id,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="555-9999",
            company="Acme Corp",
            job_title="Manager"
        )
        db.add(duplicate)
        db.commit()
        db.refresh(primary)
        db.refresh(duplicate)
        
        # Merge
        merged = ContactService.merge_contacts(
            db=db,
            primary_id=primary.id,
            duplicate_id=duplicate.id,
            user_id=test_user.id
        )
        
        # Primary should have all data
        assert merged.id == primary.id
        assert merged.email == "john@example.com"  # Primary email preserved
        assert merged.phone == "555-9999"  # Taken from duplicate
        assert merged.company == "Acme Corp"
        assert merged.job_title == "Manager"
    
    def test_reassigns_communications(self, db: Session, test_user: User):
        """Should reassign all communications from duplicate to primary"""
        # Create contacts
        primary = Contact(user_id=test_user.id, first_name="John", email="john@example.com")
        duplicate = Contact(user_id=test_user.id, first_name="John", email="john2@example.com")
        db.add(primary)
        db.add(duplicate)
        db.commit()
        
        # Create communications for duplicate
        from datetime import datetime
        now = datetime.utcnow()
        
        comm1 = CommunicationLog(
            user_id=test_user.id,
            contact_id=duplicate.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            occurred_at=now
        )
        comm2 = CommunicationLog(
            user_id=test_user.id,
            contact_id=duplicate.id,
            communication_type=CommunicationType.SMS,
            direction=CommunicationDirection.OUTBOUND,
            occurred_at=now
        )
        db.add(comm1)
        db.add(comm2)
        db.commit()
        
        # Merge
        ContactService.merge_contacts(
            db=db,
            primary_id=primary.id,
            duplicate_id=duplicate.id,
            user_id=test_user.id
        )
        
        # All communications should now point to primary
        comms = db.query(CommunicationLog).filter(
            CommunicationLog.contact_id == primary.id
        ).all()
        assert len(comms) == 2
        
        # Duplicate should be deleted
        assert db.query(Contact).filter(Contact.id == duplicate.id).first() is None
    
    def test_merges_tags(self, db: Session, test_user: User):
        """Should merge tags from both contacts"""
        primary = Contact(
            user_id=test_user.id,
            first_name="John",
            email="john@example.com",
            tags=["vip", "buyer"]
        )
        duplicate = Contact(
            user_id=test_user.id,
            first_name="John",
            email="john2@example.com",
            tags=["seller", "referral"]
        )
        db.add(primary)
        db.add(duplicate)
        db.commit()
        
        merged = ContactService.merge_contacts(
            db=db,
            primary_id=primary.id,
            duplicate_id=duplicate.id,
            user_id=test_user.id
        )
        
        # Should have all unique tags
        assert set(merged.tags) == {"vip", "buyer", "seller", "referral"}
    
    def test_prevents_merging_unowned_contacts(self, db: Session, test_user: User):
        """Should raise error if user doesn't own the contacts"""
        other_user = User(email="other@example.com", hashed_password="hashed", full_name="Other User")
        db.add(other_user)
        db.commit()
        
        primary = Contact(user_id=test_user.id, first_name="John", email="john@example.com")
        duplicate = Contact(user_id=other_user.id, first_name="Jane", email="jane@example.com")
        db.add(primary)
        db.add(duplicate)
        db.commit()
        
        with pytest.raises(ValidationException, match="don't own"):
            ContactService.merge_contacts(
                db=db,
                primary_id=primary.id,
                duplicate_id=duplicate.id,
                user_id=test_user.id
            )


class TestDetectDuplicates:
    """Test duplicate detection"""
    
    def test_finds_email_duplicates(self, db: Session, test_user: User, test_contact: Contact):
        """Should find contacts with same email"""
        duplicate = Contact(
            user_id=test_user.id,
            first_name="Jane",
            last_name="Smith",
            email=test_contact.email  # Same email
        )
        db.add(duplicate)
        db.commit()
        
        duplicates = ContactService.detect_duplicates(db, test_user.id, test_contact)
        
        assert len(duplicates) == 1
        assert duplicates[0].id == duplicate.id
    
    def test_finds_phone_duplicates(self, db: Session, test_user: User, test_contact: Contact):
        """Should find contacts with same phone"""
        duplicate = Contact(
            user_id=test_user.id,
            first_name="Jane",
            email="different@example.com",
            phone=test_contact.phone  # Same phone
        )
        db.add(duplicate)
        db.commit()
        
        duplicates = ContactService.detect_duplicates(db, test_user.id, test_contact)
        
        assert len(duplicates) == 1
        assert duplicates[0].id == duplicate.id
    
    def test_finds_name_duplicates(self, db: Session, test_user: User, test_contact: Contact):
        """Should find contacts with same first and last name"""
        duplicate = Contact(
            user_id=test_user.id,
            first_name=test_contact.first_name,
            last_name=test_contact.last_name,
            email="different@example.com"
        )
        db.add(duplicate)
        db.commit()
        
        duplicates = ContactService.detect_duplicates(db, test_user.id, test_contact)
        
        assert len(duplicates) == 1
        assert duplicates[0].id == duplicate.id

