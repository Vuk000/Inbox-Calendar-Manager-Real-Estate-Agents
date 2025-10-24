"""
Unit Tests for ContactService
Tests core contact service methods in isolation
"""
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.models.contact import Contact
from app.models.communication_log import CommunicationLog, CommunicationType, CommunicationDirection
from app.services.contact_service import ContactService
from app.shared.exceptions import ValidationException


class TestGetOrCreateContactByEmail:
    """Test get_or_create_contact_by_email method"""
    
    def test_creates_new_contact_with_full_name(self, db: Session, test_user):
        """Test creating a new contact with full name parsing"""
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="john.doe@example.com",
            user_id=test_user.id,
            sender_name="John Doe"
        )
        
        assert contact is not None
        assert contact.id is not None
        assert contact.email == "john.doe@example.com"
        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
        assert contact.user_id == test_user.id
        assert contact.contact_type == "lead"
        assert contact.lead_source == "email"
    
    def test_creates_new_contact_with_complex_name(self, db: Session, test_user):
        """Test creating contact with multi-part last name"""
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="mary.vander.pool@example.com",
            user_id=test_user.id,
            sender_name="Mary Van Der Pool"
        )
        
        assert contact.first_name == "Mary"
        assert contact.last_name == "Van Der Pool"
    
    def test_creates_new_contact_with_email_in_name(self, db: Session, test_user):
        """Test creating contact when email is included in sender_name"""
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="alice@example.com",
            user_id=test_user.id,
            sender_name="Alice Smith <alice@example.com>"
        )
        
        assert contact.first_name == "Alice"
        assert contact.last_name == "Smith"
        assert contact.email == "alice@example.com"
    
    def test_creates_new_contact_without_sender_name(self, db: Session, test_user):
        """Test creating contact without sender_name defaults to 'Unknown'"""
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="unknown@example.com",
            user_id=test_user.id,
            sender_name=None
        )
        
        assert contact.first_name == "Unknown"
        assert contact.last_name is None
        assert contact.email == "unknown@example.com"
    
    def test_creates_new_contact_with_single_name(self, db: Session, test_user):
        """Test creating contact with only first name"""
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="madonna@example.com",
            user_id=test_user.id,
            sender_name="Madonna"
        )
        
        assert contact.first_name == "Madonna"
        assert contact.last_name is None
    
    def test_returns_existing_contact_same_email(self, db: Session, test_user):
        """Test that existing contact is returned instead of creating duplicate"""
        # Create existing contact
        existing = Contact(
            user_id=test_user.id,
            email="existing@example.com",
            first_name="Existing",
            last_name="Contact",
            contact_type="buyer"
        )
        db.add(existing)
        db.commit()
        existing_id = existing.id
        
        # Try to get or create with same email
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="existing@example.com",
            user_id=test_user.id,
            sender_name="Different Name"
        )
        
        # Should return the same contact
        assert contact.id == existing_id
        assert contact.first_name == "Existing"  # Name should NOT change
        assert contact.last_name == "Contact"
        assert contact.contact_type == "buyer"  # Type should NOT change
        
        # Verify no duplicate was created
        count = db.query(Contact).filter(
            Contact.user_id == test_user.id,
            Contact.email == "existing@example.com"
        ).count()
        assert count == 1
    
    def test_different_users_can_have_same_email_contact(self, db: Session, test_user):
        """Test that different users can have contacts with the same email"""
        # Create second user
        user2 = User(
            email="user2@example.com",
            hashed_password="hashed",
            full_name="User Two"
        )
        db.add(user2)
        db.commit()
        
        # User 1 creates contact
        contact1 = ContactService.get_or_create_contact_by_email(
            db=db,
            email="shared@example.com",
            user_id=test_user.id,
            sender_name="Shared Contact"
        )
        
        # User 2 creates contact with same email
        contact2 = ContactService.get_or_create_contact_by_email(
            db=db,
            email="shared@example.com",
            user_id=user2.id,
            sender_name="Shared Contact"
        )
        
        # Should be different contacts
        assert contact1.id != contact2.id
        assert contact1.user_id == test_user.id
        assert contact2.user_id == user2.id
        assert contact1.email == contact2.email


class TestContactSearch:
    """Test contact search functionality"""
    
    @pytest.fixture
    def sample_contacts(self, db: Session, test_user):
        """Create sample contacts for search testing"""
        contacts = [
            Contact(
                user_id=test_user.id,
                first_name="Alice",
                last_name="Anderson",
                email="alice.anderson@example.com",
                phone="555-1111",
                company="ABC Realty",
                contact_type="buyer"
            ),
            Contact(
                user_id=test_user.id,
                first_name="Bob",
                last_name="Brown",
                email="bob@brownproperties.com",
                phone="555-2222",
                company="Brown Properties",
                contact_type="seller"
            ),
            Contact(
                user_id=test_user.id,
                first_name="Charlie",
                last_name="Chen",
                email="charlie.chen@gmail.com",
                phone="555-3333",
                company="Tech Startup Inc",
                contact_type="lead"
            ),
            Contact(
                user_id=test_user.id,
                first_name="Diana",
                last_name="Davis",
                email="diana@example.com",
                phone="555-4444",
                company="ABC Realty",
                contact_type="buyer"
            )
        ]
        
        for contact in contacts:
            db.add(contact)
        db.commit()
        
        return contacts
    
    def test_search_by_first_name(self, db: Session, test_user, sample_contacts):
        """Test searching contacts by first name"""
        results = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            search="Alice"
        )
        
        assert len(results) == 1
        assert results[0].first_name == "Alice"
    
    def test_search_by_last_name(self, db: Session, test_user, sample_contacts):
        """Test searching contacts by last name"""
        results = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            search="Brown"
        )
        
        assert len(results) == 1
        assert results[0].last_name == "Brown"
    
    def test_search_by_email(self, db: Session, test_user, sample_contacts):
        """Test searching contacts by email"""
        results = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            search="gmail.com"
        )
        
        assert len(results) == 1
        assert "gmail.com" in results[0].email
    
    def test_search_by_phone(self, db: Session, test_user, sample_contacts):
        """Test searching contacts by phone number"""
        results = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            search="555-2222"
        )
        
        assert len(results) == 1
        assert results[0].phone == "555-2222"
    
    def test_search_by_company(self, db: Session, test_user, sample_contacts):
        """Test searching contacts by company name"""
        results = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            search="ABC Realty"
        )
        
        assert len(results) == 2
        assert all(c.company == "ABC Realty" for c in results)
    
    def test_search_case_insensitive(self, db: Session, test_user, sample_contacts):
        """Test that search is case-insensitive"""
        results = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            search="alice"
        )
        
        assert len(results) == 1
        assert results[0].first_name == "Alice"
    
    def test_filter_by_contact_type(self, db: Session, test_user, sample_contacts):
        """Test filtering by contact type"""
        results = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            contact_type="buyer"
        )
        
        assert len(results) == 2
        assert all(c.contact_type == "buyer" for c in results)
    
    def test_filter_by_contact_status(self, db: Session, test_user, sample_contacts):
        """Test filtering by contact status"""
        results = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            contact_status="active"
        )
        
        # All sample contacts are active by default
        assert len(results) == 4
    
    def test_search_with_no_results(self, db: Session, test_user, sample_contacts):
        """Test search that returns no results"""
        results = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            search="nonexistent@nowhere.com"
        )
        
        assert len(results) == 0
    
    def test_pagination(self, db: Session, test_user, sample_contacts):
        """Test pagination parameters"""
        # Get first 2
        page1 = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            skip=0,
            limit=2
        )
        
        assert len(page1) == 2
        
        # Get next 2
        page2 = ContactService.list_contacts(
            db=db,
            user_id=test_user.id,
            skip=2,
            limit=2
        )
        
        assert len(page2) == 2
        
        # Verify different contacts
        page1_ids = {c.id for c in page1}
        page2_ids = {c.id for c in page2}
        assert page1_ids.isdisjoint(page2_ids)


class TestRelationshipScoreCalculation:
    """Test relationship score calculation"""
    
    def test_relationship_score_increases_with_communications(self, db: Session, test_user):
        """Test that relationship score is influenced by number of communications"""
        contact = Contact(
            user_id=test_user.id,
            first_name="Score",
            last_name="Test",
            email="score@example.com"
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        initial_score = contact.relationship_score
        
        # Add communications
        base_time = datetime.utcnow()
        for i in range(10):
            comm = CommunicationLog(
                user_id=test_user.id,
                contact_id=contact.id,
                communication_type=CommunicationType.EMAIL,
                direction=CommunicationDirection.INBOUND,
                body=f"Communication {i}",
                from_address="score@example.com",
                occurred_at=base_time - timedelta(days=i)
            )
            db.add(comm)
        
        db.commit()
        
        # Update relationship score
        ContactService.update_relationship_score(db, contact.id)
        db.refresh(contact)
        
        # Score should increase
        assert contact.relationship_score > initial_score
        assert contact.contact_frequency == 10
    
    def test_relationship_score_decreases_with_time(self, db: Session, test_user):
        """Test that relationship score considers recency"""
        contact = Contact(
            user_id=test_user.id,
            first_name="Recency",
            last_name="Test",
            email="recency@example.com"
        )
        db.add(contact)
        db.commit()
        
        # Add old communication
        old_comm = CommunicationLog(
            user_id=test_user.id,
            contact_id=contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            body="Old communication",
            from_address="recency@example.com",
            occurred_at=datetime.utcnow() - timedelta(days=365)  # 1 year ago
        )
        db.add(old_comm)
        db.commit()
        
        ContactService.update_relationship_score(db, contact.id)
        db.refresh(contact)
        old_score = contact.relationship_score
        
        # Add recent communication
        recent_comm = CommunicationLog(
            user_id=test_user.id,
            contact_id=contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            body="Recent communication",
            from_address="recency@example.com",
            occurred_at=datetime.utcnow()
        )
        db.add(recent_comm)
        db.commit()
        
        ContactService.update_relationship_score(db, contact.id)
        db.refresh(contact)
        new_score = contact.relationship_score
        
        # Score should increase with recent activity
        assert new_score > old_score
        assert contact.last_contact_date is not None


class TestContactCRUD:
    """Test basic CRUD operations"""
    
    def test_create_contact(self, db: Session, test_user):
        """Test creating a contact"""
        contact_data = {
            "first_name": "Test",
            "last_name": "Contact",
            "email": "test@example.com",
            "phone": "555-9999",
            "contact_type": "buyer"
        }
        
        contact = ContactService.create_contact(
            db=db,
            user_id=test_user.id,
            contact_data=contact_data
        )
        
        assert contact.id is not None
        assert contact.first_name == "Test"
        assert contact.email == "test@example.com"
        assert contact.user_id == test_user.id
    
    def test_get_contact(self, db: Session, test_user):
        """Test retrieving a contact"""
        contact = Contact(
            user_id=test_user.id,
            first_name="Get",
            last_name="Test",
            email="get@example.com"
        )
        db.add(contact)
        db.commit()
        
        retrieved = ContactService.get_contact(db, contact.id, test_user.id)
        
        assert retrieved is not None
        assert retrieved.id == contact.id
        assert retrieved.email == "get@example.com"
    
    def test_update_contact(self, db: Session, test_user):
        """Test updating a contact"""
        contact = Contact(
            user_id=test_user.id,
            first_name="Original",
            last_name="Name",
            email="update@example.com"
        )
        db.add(contact)
        db.commit()
        
        update_data = {
            "first_name": "Updated",
            "phone": "555-1234"
        }
        
        updated = ContactService.update_contact(
            db=db,
            contact_id=contact.id,
            user_id=test_user.id,
            update_data=update_data
        )
        
        assert updated.first_name == "Updated"
        assert updated.last_name == "Name"  # Unchanged
        assert updated.phone == "555-1234"
    
    def test_delete_contact(self, db: Session, test_user):
        """Test deleting a contact"""
        contact = Contact(
            user_id=test_user.id,
            first_name="Delete",
            last_name="Test",
            email="delete@example.com"
        )
        db.add(contact)
        db.commit()
        contact_id = contact.id
        
        success = ContactService.delete_contact(db, contact_id, test_user.id)
        
        assert success is True
        
        # Verify contact is deleted
        deleted = db.query(Contact).filter(Contact.id == contact_id).first()
        assert deleted is None

