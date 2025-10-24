"""
Email Sync Integration Tests
Tests the critical pipeline: Email → Contact + CommunicationLog
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.communication_log import CommunicationLog, CommunicationType, CommunicationDirection
from app.models.email_account import EmailAccount, EmailProvider, SyncStatus
from app.services.contact_service import ContactService
from app.tasks.email_sync_task import sync_gmail_account, process_email_with_ai


class TestEmailSyncIntegration:
    """Test email synchronization creates contacts and communication logs"""
    
    @pytest.fixture
    def email_account(self, db: Session, test_user):
        """Create a test Gmail account"""
        from app.security.encryption import encrypt_data
        
        account = EmailAccount(
            user_id=test_user.id,
            email="test@gmail.com",
            provider=EmailProvider.GMAIL,
            is_active=True,
            auto_sync_enabled=True,
            encrypted_access_token=encrypt_data("mock-access-token"),
            encrypted_refresh_token=encrypt_data("mock-refresh-token"),
            sync_status=SyncStatus.IDLE
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    
    @pytest.fixture
    def mock_gmail_messages(self):
        """Mock Gmail API responses"""
        return {
            "list_response": {
                "messages": [
                    {"id": "msg_001"},
                    {"id": "msg_002"}
                ],
                "next_page_token": None,
                "result_size_estimate": 2
            },
            "message_details": {
                "msg_001": {
                    "id": "msg_001",
                    "thread_id": "thread_001",
                    "subject": "Interested in 123 Main St",
                    "from": "John Buyer <john.buyer@example.com>",
                    "from_name": "John Buyer",
                    "to": "test@gmail.com",
                    "date": "2024-01-15T10:30:00Z",
                    "body": "Hi, I'm very interested in the property at 123 Main St. Can we schedule a viewing this week?",
                    "snippet": "Hi, I'm very interested in the property at 123 Main St...",
                    "has_attachments": False,
                    "attachments": []
                },
                "msg_002": {
                    "id": "msg_002",
                    "thread_id": "thread_002",
                    "subject": "Ready to make an offer",
                    "from": "Sarah Seller <sarah.seller@example.com>",
                    "from_name": "Sarah Seller",
                    "to": "test@gmail.com",
                    "date": "2024-01-15T14:20:00Z",
                    "body": "I've reviewed the comps and I'm ready to list my house. Let's discuss pricing.",
                    "snippet": "I've reviewed the comps and I'm ready to list my house...",
                    "has_attachments": True,
                    "attachments": [
                        {"filename": "house_photos.zip", "size": 2048000}
                    ]
                }
            }
        }
    
    @patch('app.tasks.email_sync_task.GmailIntegration')
    @patch('app.tasks.email_sync_task.process_email_with_ai')
    @patch('app.tasks.email_sync_task.connection_manager')
    def test_gmail_sync_creates_contacts_and_communications(
        self,
        mock_connection_manager,
        mock_process_email,
        mock_gmail_class,
        db: Session,
        test_user,
        email_account,
        mock_gmail_messages
    ):
        """
        THE CRITICAL TEST: Email sync creates Contact + CommunicationLog
        
        This test validates the core pipeline:
        1. Gmail sync fetches new emails
        2. For each email, it creates or finds a Contact
        3. It creates a CommunicationLog entry linked to that Contact
        4. It triggers AI processing
        """
        # Setup Gmail API mocks
        mock_gmail = Mock()
        mock_gmail_class.return_value = mock_gmail
        
        # Mock list_messages to return 2 emails
        async def mock_list_messages(*args, **kwargs):
            return mock_gmail_messages["list_response"]
        
        mock_gmail.list_messages = AsyncMock(side_effect=mock_list_messages)
        
        # Mock get_message to return details
        async def mock_get_message(encrypted_access_token, message_id, encrypted_refresh_token=None):
            return mock_gmail_messages["message_details"].get(message_id, {})
        
        mock_gmail.get_message = AsyncMock(side_effect=mock_get_message)
        
        # Mock connection manager
        mock_connection_manager.notify_sync_status = AsyncMock()
        
        # Mock AI processing (delay method)
        mock_process_email.delay = Mock()
        
        # Verify starting state - no contacts or communications
        initial_contact_count = db.query(Contact).filter(Contact.user_id == test_user.id).count()
        initial_comm_count = db.query(CommunicationLog).filter(CommunicationLog.user_id == test_user.id).count()
        
        assert initial_contact_count == 0
        assert initial_comm_count == 0
        
        # Execute the sync task
        result = sync_gmail_account(
            user_id=test_user.id,
            account_id=email_account.id,
            db=db
        )
        
        # Verify sync result
        assert result["status"] == "success"
        assert result["processed"] == 2
        
        # CRITICAL VALIDATION 1: Two contacts were created
        contacts = db.query(Contact).filter(Contact.user_id == test_user.id).all()
        assert len(contacts) == 2
        
        # Verify contact details
        contact_emails = {c.email for c in contacts}
        assert "john.buyer@example.com" in contact_emails
        assert "sarah.seller@example.com" in contact_emails
        
        # Verify contact names were parsed correctly
        john_contact = db.query(Contact).filter(
            Contact.user_id == test_user.id,
            Contact.email == "john.buyer@example.com"
        ).first()
        assert john_contact is not None
        assert john_contact.first_name == "John"
        assert john_contact.last_name == "Buyer"
        assert john_contact.contact_type == "lead"
        assert john_contact.lead_source == "email"
        
        sarah_contact = db.query(Contact).filter(
            Contact.user_id == test_user.id,
            Contact.email == "sarah.seller@example.com"
        ).first()
        assert sarah_contact is not None
        assert sarah_contact.first_name == "Sarah"
        assert sarah_contact.last_name == "Seller"
        
        # CRITICAL VALIDATION 2: Two communication logs were created
        communications = db.query(CommunicationLog).filter(
            CommunicationLog.user_id == test_user.id
        ).all()
        assert len(communications) == 2
        
        # Verify communication log details for John's email
        john_comm = db.query(CommunicationLog).filter(
            CommunicationLog.user_id == test_user.id,
            CommunicationLog.contact_id == john_contact.id
        ).first()
        assert john_comm is not None
        assert john_comm.communication_type == CommunicationType.EMAIL
        assert john_comm.direction == CommunicationDirection.INBOUND
        assert john_comm.subject == "Interested in 123 Main St"
        assert john_comm.from_address == "john.buyer@example.com"
        assert john_comm.to_address == "test@gmail.com"
        assert john_comm.external_id == "msg_001"
        assert john_comm.has_attachments is False
        assert "interested in the property" in john_comm.body.lower()
        
        # Verify communication log details for Sarah's email
        sarah_comm = db.query(CommunicationLog).filter(
            CommunicationLog.user_id == test_user.id,
            CommunicationLog.contact_id == sarah_contact.id
        ).first()
        assert sarah_comm is not None
        assert sarah_comm.communication_type == CommunicationType.EMAIL
        assert sarah_comm.subject == "Ready to make an offer"
        assert sarah_comm.from_address == "sarah.seller@example.com"
        assert sarah_comm.has_attachments is True
        assert len(sarah_comm.attachments) == 1
        assert sarah_comm.attachments[0]["filename"] == "house_photos.zip"
        
        # CRITICAL VALIDATION 3: AI processing was triggered for both emails
        assert mock_process_email.delay.call_count == 2
        
        # Verify email account status updated
        db.refresh(email_account)
        assert email_account.sync_status == SyncStatus.IDLE
        assert email_account.last_sync_at is not None
        assert email_account.sync_error_message is None
    
    @patch('app.tasks.email_sync_task.GmailIntegration')
    @patch('app.tasks.email_sync_task.process_email_with_ai')
    @patch('app.tasks.email_sync_task.connection_manager')
    def test_gmail_sync_reuses_existing_contacts(
        self,
        mock_connection_manager,
        mock_process_email,
        mock_gmail_class,
        db: Session,
        test_user,
        email_account,
        mock_gmail_messages
    ):
        """
        Test that sync reuses existing contacts instead of creating duplicates
        """
        # Create an existing contact
        existing_contact = Contact(
            user_id=test_user.id,
            email="john.buyer@example.com",
            first_name="John",
            last_name="Buyer",
            contact_type="buyer"
        )
        db.add(existing_contact)
        db.commit()
        db.refresh(existing_contact)
        
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail_class.return_value = mock_gmail
        
        async def mock_list_messages(*args, **kwargs):
            return {"messages": [{"id": "msg_001"}], "next_page_token": None}
        
        async def mock_get_message(encrypted_access_token, message_id, encrypted_refresh_token=None):
            return mock_gmail_messages["message_details"]["msg_001"]
        
        mock_gmail.list_messages = AsyncMock(side_effect=mock_list_messages)
        mock_gmail.get_message = AsyncMock(side_effect=mock_get_message)
        mock_connection_manager.notify_sync_status = AsyncMock()
        mock_process_email.delay = Mock()
        
        # Execute sync
        result = sync_gmail_account(
            user_id=test_user.id,
            account_id=email_account.id,
            db=db
        )
        
        assert result["status"] == "success"
        
        # Verify only 1 contact exists (the existing one)
        contacts = db.query(Contact).filter(
            Contact.user_id == test_user.id,
            Contact.email == "john.buyer@example.com"
        ).all()
        assert len(contacts) == 1
        assert contacts[0].id == existing_contact.id
        
        # Verify communication log was created and linked to existing contact
        comm = db.query(CommunicationLog).filter(
            CommunicationLog.user_id == test_user.id,
            CommunicationLog.contact_id == existing_contact.id
        ).first()
        assert comm is not None
        assert comm.subject == "Interested in 123 Main St"
    
    @patch('app.tasks.email_sync_task.GmailIntegration')
    def test_gmail_sync_skips_duplicate_emails(
        self,
        mock_gmail_class,
        db: Session,
        test_user,
        email_account,
        mock_gmail_messages
    ):
        """
        Test that already-synced emails are skipped based on external_id
        """
        # Create existing communication log
        existing_contact = Contact(
            user_id=test_user.id,
            email="john.buyer@example.com",
            first_name="John",
            last_name="Buyer"
        )
        db.add(existing_contact)
        db.commit()
        
        existing_comm = CommunicationLog(
            user_id=test_user.id,
            contact_id=existing_contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            external_id="msg_001",  # Same as what sync will find
            subject="Already synced",
            from_address="john.buyer@example.com",
            occurred_at=datetime.utcnow()
        )
        db.add(existing_comm)
        db.commit()
        
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail_class.return_value = mock_gmail
        
        async def mock_list_messages(*args, **kwargs):
            return {"messages": [{"id": "msg_001"}], "next_page_token": None}
        
        mock_gmail.list_messages = AsyncMock(side_effect=mock_list_messages)
        
        # Execute sync
        result = sync_gmail_account(
            user_id=test_user.id,
            account_id=email_account.id,
            db=db
        )
        
        assert result["status"] == "success"
        assert result["processed"] == 0  # Should skip the duplicate
        
        # Verify only 1 communication log exists
        comm_count = db.query(CommunicationLog).filter(
            CommunicationLog.user_id == test_user.id,
            CommunicationLog.external_id == "msg_001"
        ).count()
        assert comm_count == 1
    
    @patch('app.tasks.email_sync_task.TriageAgent')
    def test_ai_processing_adds_scores(
        self,
        mock_triage_agent_class,
        db: Session,
        test_user
    ):
        """
        Test that AI processing adds urgency and sentiment scores
        """
        # Create a contact and communication log
        contact = Contact(
            user_id=test_user.id,
            email="buyer@example.com",
            first_name="Test",
            last_name="Buyer"
        )
        db.add(contact)
        db.commit()
        
        comm_log = CommunicationLog(
            user_id=test_user.id,
            contact_id=contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            subject="URGENT: Need to see property TODAY",
            body="This is an urgent request. I need to see the property immediately!",
            from_address="buyer@example.com",
            occurred_at=datetime.utcnow()
        )
        db.add(comm_log)
        db.commit()
        db.refresh(comm_log)
        
        # Verify no AI scores initially
        assert comm_log.urgency_score is None
        assert comm_log.sentiment_score is None
        
        # Setup AI mock
        mock_agent = Mock()
        mock_triage_agent_class.return_value = mock_agent
        
        async def mock_analyze_email(email_data):
            return {
                "urgency_score": 85.0,
                "sentiment_score": 0.3,
                "entities": {"intent": "viewing_request", "urgency": "high"}
            }
        
        mock_agent.analyze_email = AsyncMock(side_effect=mock_analyze_email)
        
        # Process with AI
        result = process_email_with_ai(comm_log.id, db=db)
        
        assert result["status"] == "success"
        
        # Verify AI scores were added
        db.refresh(comm_log)
        assert comm_log.urgency_score == 85.0
        assert comm_log.sentiment_score == 0.3
        assert comm_log.key_topics == {"intent": "viewing_request", "urgency": "high"}
    
    def test_get_or_create_contact_by_email_creates_new(self, db: Session, test_user):
        """Test ContactService.get_or_create_contact_by_email creates new contact"""
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="newlead@example.com",
            user_id=test_user.id,
            sender_name="Jane Lead"
        )
        
        assert contact is not None
        assert contact.email == "newlead@example.com"
        assert contact.first_name == "Jane"
        assert contact.last_name == "Lead"
        assert contact.user_id == test_user.id
    
    def test_get_or_create_contact_by_email_returns_existing(self, db: Session, test_user):
        """Test ContactService.get_or_create_contact_by_email returns existing contact"""
        # Create existing contact
        existing = Contact(
            user_id=test_user.id,
            email="existing@example.com",
            first_name="Existing",
            last_name="Contact"
        )
        db.add(existing)
        db.commit()
        existing_id = existing.id
        
        # Try to get or create
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="existing@example.com",
            user_id=test_user.id,
            sender_name="Different Name"
        )
        
        # Should return the same contact, not create a new one
        assert contact.id == existing_id
        assert contact.first_name == "Existing"  # Name should not change
        
        # Verify no duplicate was created
        count = db.query(Contact).filter(
            Contact.user_id == test_user.id,
            Contact.email == "existing@example.com"
        ).count()
        assert count == 1

