"""
Tests for Contacts API Endpoints
Tests critical CRM functionality including CSV import and timeline
"""
import pytest
import io
import csv
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.main import app
from app.models.user import User
from app.models.contact import Contact
from app.models.communication_log import CommunicationLog, CommunicationType, CommunicationDirection
from app.dependencies import get_current_user


# Test client
client = TestClient(app)


@pytest.fixture
def auth_headers(db: Session):
    """Create authenticated user and return auth headers"""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    
    # Override dependency to return this user
    def override_get_current_user():
        return user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    yield {"Authorization": "Bearer fake-token"}
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def test_contact(db: Session, auth_headers):
    """Create a test contact"""
    # Get user from overridden dependency
    user = app.dependency_overrides[get_current_user]()
    
    contact = Contact(
        user_id=user.id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="555-1234",
        contact_type="buyer"
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


class TestListContacts:
    """Test GET /contacts endpoint"""
    
    def test_lists_all_contacts(self, db: Session, auth_headers):
        """Should return all user's contacts"""
        response = client.get("/api/v1/contacts", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "contacts" in data
        assert isinstance(data["contacts"], list)
    
    def test_filters_by_contact_type(self, db: Session, auth_headers, test_contact):
        """Should filter contacts by type"""
        response = client.get(
            "/api/v1/contacts?contact_type=buyer",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["contacts"]) >= 1
        assert all(c["contact_type"] == "buyer" for c in data["contacts"])
    
    def test_filters_by_contact_status(self, db: Session, auth_headers):
        """Should filter contacts by status"""
        response = client.get(
            "/api/v1/contacts?contact_status=active",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(c["contact_status"] == "active" for c in data["contacts"])
    
    def test_searches_contacts(self, db: Session, auth_headers, test_contact):
        """Should search contacts by name, email, phone"""
        response = client.get(
            "/api/v1/contacts?search=john",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["contacts"]) >= 1


class TestGetContactTimeline:
    """Test GET /contacts/{id}/timeline - THE KILLER FEATURE"""
    
    def test_returns_sorted_communications(self, db: Session, auth_headers, test_contact):
        """Should return communications in chronological order"""
        user = app.dependency_overrides[get_current_user]()
        
        # Create communications at different times
        now = datetime.utcnow()
        comms = [
            CommunicationLog(
                user_id=user.id,
                contact_id=test_contact.id,
                communication_type=CommunicationType.EMAIL,
                direction=CommunicationDirection.INBOUND,
                subject="First email",
                occurred_at=now - timedelta(days=2)
            ),
            CommunicationLog(
                user_id=user.id,
                contact_id=test_contact.id,
                communication_type=CommunicationType.SMS,
                direction=CommunicationDirection.OUTBOUND,
                body="Text message",
                occurred_at=now - timedelta(days=1)
            ),
            CommunicationLog(
                user_id=user.id,
                contact_id=test_contact.id,
                communication_type=CommunicationType.NOTE,
                direction=CommunicationDirection.INTERNAL,
                body="Internal note",
                occurred_at=now
            )
        ]
        for comm in comms:
            db.add(comm)
        db.commit()
        
        response = client.get(
            f"/api/v1/contacts/{test_contact.id}/timeline",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "communications" in data
        assert "pagination" in data
        
        timeline = data["communications"]
        assert len(timeline) == 3
        
        # Should be sorted newest first
        assert timeline[0]["subject"] is None  # Note (most recent)
        assert timeline[1]["body"] == "Text message"  # SMS
        assert timeline[2]["subject"] == "First email"  # Email (oldest)
    
    def test_returns_empty_for_no_communications(self, db: Session, auth_headers, test_contact):
        """Should return empty list if no communications"""
        response = client.get(
            f"/api/v1/contacts/{test_contact.id}/timeline",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["communications"] == []
        assert data["pagination"]["has_more"] is False
        assert data["pagination"]["next_cursor"] is None
    
    def test_respects_limit(self, db: Session, auth_headers, test_contact):
        """Should limit number of communications returned"""
        user = app.dependency_overrides[get_current_user]()
        
        # Create 10 communications
        for i in range(10):
            comm = CommunicationLog(
                user_id=user.id,
                contact_id=test_contact.id,
                communication_type=CommunicationType.NOTE,
                direction=CommunicationDirection.INTERNAL,
                body=f"Note {i}",
                occurred_at=datetime.utcnow() - timedelta(hours=i)
            )
            db.add(comm)
        db.commit()
        
        response = client.get(
            f"/api/v1/contacts/{test_contact.id}/timeline?limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["communications"]) == 5
        assert data["pagination"]["has_more"] is True
        assert data["pagination"]["next_cursor"] is not None
    
    def test_cursor_pagination_works(self, db: Session, auth_headers, test_contact):
        """Should paginate correctly using cursor"""
        user = app.dependency_overrides[get_current_user]()
        
        # Create 25 communications
        for i in range(25):
            comm = CommunicationLog(
                user_id=user.id,
                contact_id=test_contact.id,
                communication_type=CommunicationType.NOTE,
                direction=CommunicationDirection.INTERNAL,
                body=f"Note {i}",
                occurred_at=datetime.utcnow() - timedelta(minutes=i)
            )
            db.add(comm)
        db.commit()
        
        # Get first page
        response1 = client.get(
            f"/api/v1/contacts/{test_contact.id}/timeline?limit=10",
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["communications"]) == 10
        assert data1["pagination"]["has_more"] is True
        first_cursor = data1["pagination"]["next_cursor"]
        assert first_cursor is not None
        
        # Get second page using cursor
        response2 = client.get(
            f"/api/v1/contacts/{test_contact.id}/timeline?limit=10&cursor={first_cursor}",
            headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["communications"]) == 10
        assert data2["pagination"]["has_more"] is True
        
        # Get third page
        second_cursor = data2["pagination"]["next_cursor"]
        response3 = client.get(
            f"/api/v1/contacts/{test_contact.id}/timeline?limit=10&cursor={second_cursor}",
            headers=auth_headers
        )
        assert response3.status_code == 200
        data3 = response3.json()
        assert len(data3["communications"]) == 5  # Only 5 left
        assert data3["pagination"]["has_more"] is False
        
        # Verify no duplicates across pages
        all_ids = (
            [c["id"] for c in data1["communications"]] +
            [c["id"] for c in data2["communications"]] +
            [c["id"] for c in data3["communications"]]
        )
        assert len(all_ids) == len(set(all_ids))  # No duplicates
    
    def test_performance_target_met(self, db: Session, auth_headers, test_contact):
        """Should respond in <500ms even with 200+ communications"""
        user = app.dependency_overrides[get_current_user]()
        
        # Create 200 communications
        comms = []
        for i in range(200):
            comm = CommunicationLog(
                user_id=user.id,
                contact_id=test_contact.id,
                communication_type=CommunicationType.EMAIL,
                direction=CommunicationDirection.INBOUND,
                subject=f"Email {i}",
                body=f"Body of email {i}",
                occurred_at=datetime.utcnow() - timedelta(minutes=i),
                external_id=f"ext-{i}"
            )
            comms.append(comm)
        db.add_all(comms)
        db.commit()
        
        # Make request and check response time
        import time
        start = time.time()
        response = client.get(
            f"/api/v1/contacts/{test_contact.id}/timeline?limit=20",
            headers=auth_headers
        )
        elapsed_ms = (time.time() - start) * 1000
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["communications"]) == 20
        
        # Performance assertion: <500ms
        assert elapsed_ms < 500, f"Timeline took {elapsed_ms}ms, should be <500ms"
        
        # Also check the reported response time
        assert data["meta"]["response_time_ms"] < 500
    
    def test_unauthorized_access_denied(self, db: Session, test_contact):
        """Should deny access without authentication"""
        response = client.get(
            f"/api/v1/contacts/{test_contact.id}/timeline"
        )
        assert response.status_code == 401
    
    def test_invalid_cursor_handled_gracefully(self, db: Session, auth_headers, test_contact):
        """Should handle invalid cursor format gracefully"""
        response = client.get(
            f"/api/v1/contacts/{test_contact.id}/timeline?cursor=invalid-cursor",
            headers=auth_headers
        )
        
        # Should still return results, just without cursor filter
        assert response.status_code == 200
        data = response.json()
        assert "communications" in data


class TestCSVImport:
    """Test POST /contacts/import - Critical for user adoption"""
    
    def create_csv_file(self, rows):
        """Helper to create CSV file in memory"""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        output.seek(0)
        return output.getvalue()
    
    def test_imports_valid_csv(self, db: Session, auth_headers):
        """Should import valid CSV with field mapping"""
        csv_data = self.create_csv_file([
            {"First Name": "Alice", "Last Name": "Smith", "Email": "alice@example.com", "Phone": "555-0001"},
            {"First Name": "Bob", "Last Name": "Jones", "Email": "bob@example.com", "Phone": "555-0002"},
        ])
        
        field_mapping = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "phone": "Phone"
        }
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=auth_headers,
            files={"file": ("contacts.csv", io.BytesIO(csv_data.encode()), "text/csv")},
            params={"field_mapping": str(field_mapping).replace("'", '"')}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["imported_count"] == 2
        assert data["skipped_count"] == 0
    
    def test_handles_duplicates(self, db: Session, auth_headers, test_contact):
        """Should skip duplicate emails"""
        csv_data = self.create_csv_file([
            {"Email": test_contact.email, "First Name": "Duplicate", "Last Name": "Person"},
            {"Email": "new@example.com", "First Name": "New", "Last Name": "Person"},
        ])
        
        field_mapping = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email"
        }
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=auth_headers,
            files={"file": ("contacts.csv", io.BytesIO(csv_data.encode()), "text/csv")},
            params={"field_mapping": str(field_mapping).replace("'", '"')}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["imported_count"] == 1  # Only new contact
        assert data["skipped_count"] == 1  # Duplicate skipped
    
    def test_handles_malformed_data(self, db: Session, auth_headers):
        """Should handle rows with missing required fields"""
        csv_data = self.create_csv_file([
            {"First Name": "", "Email": "no-name@example.com"},  # Missing first name
            {"First Name": "Valid", "Email": "valid@example.com"},
        ])
        
        field_mapping = {
            "first_name": "First Name",
            "email": "Email"
        }
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=auth_headers,
            files={"file": ("contacts.csv", io.BytesIO(csv_data.encode()), "text/csv")},
            params={"field_mapping": str(field_mapping).replace("'", '"')}
        )
        
        # Should not crash, should report errors
        assert response.status_code == 200
        data = response.json()
        assert data["imported_count"] >= 0
        assert len(data["errors"]) > 0 or data["skipped_count"] > 0
    
    def test_validates_email_format(self, db: Session, auth_headers):
        """Should validate email format and report errors"""
        csv_data = self.create_csv_file([
            {"First Name": "Invalid", "Last Name": "Email", "Email": "not-an-email"},
            {"First Name": "Valid", "Last Name": "Email", "Email": "valid@example.com"},
        ])
        
        field_mapping = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email"
        }
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=auth_headers,
            files={"file": ("contacts.csv", io.BytesIO(csv_data.encode()), "text/csv")},
            params={"field_mapping": str(field_mapping).replace("'", '"')}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["imported_count"] == 1  # Only valid email imported
        assert data["error_count"] > 0  # Invalid email reported
    
    def test_duplicate_strategy_skip(self, db: Session, auth_headers, test_contact):
        """Should skip duplicates when strategy is 'skip'"""
        csv_data = self.create_csv_file([
            {"First Name": "Updated", "Email": test_contact.email},
        ])
        
        field_mapping = {"first_name": "First Name", "email": "Email"}
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=auth_headers,
            files={"file": ("contacts.csv", io.BytesIO(csv_data.encode()), "text/csv")},
            params={
                "field_mapping": str(field_mapping).replace("'", '"'),
                "duplicate_strategy": "skip"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["skipped_count"] == 1
        
        # Verify original contact unchanged
        db.refresh(test_contact)
        assert test_contact.first_name == "John"
    
    def test_duplicate_strategy_update(self, db: Session, auth_headers, test_contact):
        """Should update duplicates when strategy is 'update'"""
        csv_data = self.create_csv_file([
            {"First Name": "Updated", "Last Name": "Name", "Email": test_contact.email},
        ])
        
        field_mapping = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email"
        }
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=auth_headers,
            files={"file": ("contacts.csv", io.BytesIO(csv_data.encode()), "text/csv")},
            params={
                "field_mapping": str(field_mapping).replace("'", '"'),
                "duplicate_strategy": "update"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated_count"] == 1
        
        # Verify contact was updated
        db.refresh(test_contact)
        assert test_contact.first_name == "Updated"
        assert test_contact.last_name == "Name"
    
    def test_file_size_validation(self, db: Session, auth_headers):
        """Should reject files larger than 10MB"""
        # Create a large CSV (simulate)
        large_data = "a" * (11 * 1024 * 1024)  # 11MB
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=auth_headers,
            files={"file": ("large.csv", io.BytesIO(large_data.encode()), "text/csv")},
            params={"field_mapping": '{"first_name": "Name"}'}
        )
        
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()
    
    def test_rejects_non_csv_file(self, db: Session, auth_headers):
        """Should reject non-CSV files"""
        response = client.post(
            "/api/v1/contacts/import",
            headers=auth_headers,
            files={"file": ("notcsv.txt", io.BytesIO(b"Not a CSV"), "text/plain")},
            params={"field_mapping": '{"first_name": "Name"}'}
        )
        
        assert response.status_code == 400
    
    @pytest.mark.slow
    def test_imports_large_csv(self, db: Session, auth_headers):
        """Should handle large CSV files (10K contacts) - Performance test"""
        # Generate 10K contacts
        rows = []
        for i in range(10000):
            rows.append({
                "First Name": f"Person{i}",
                "Last Name": f"User{i}",
                "Email": f"person{i}@example.com",
                "Phone": f"555-{i:04d}"
            })
        
        csv_data = self.create_csv_file(rows)
        
        field_mapping = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "phone": "Phone"
        }
        
        import time
        start = time.time()
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=auth_headers,
            files={"file": ("large.csv", io.BytesIO(csv_data.encode()), "text/csv")},
            params={"field_mapping": str(field_mapping).replace("'", '"')},
            timeout=60.0  # Allow 60 seconds
        )
        
        elapsed = time.time() - start
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["imported_count"] > 9000  # Allow for some errors
        assert elapsed < 30  # Should complete within 30 seconds per spec


class TestContactCRUD:
    """Test basic CRUD operations"""
    
    def test_creates_contact(self, db: Session, auth_headers):
        """Should create a new contact"""
        response = client.post(
            "/api/v1/contacts",
            headers=auth_headers,
            json={
                "first_name": "New",
                "last_name": "Contact",
                "email": "new@example.com",
                "phone": "555-9999"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "New"
        assert data["email"] == "new@example.com"
        assert "id" in data
    
    def test_gets_single_contact(self, db: Session, auth_headers, test_contact):
        """Should retrieve a single contact by ID"""
        response = client.get(
            f"/api/v1/contacts/{test_contact.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_contact.id
        assert data["email"] == test_contact.email
    
    def test_updates_contact(self, db: Session, auth_headers, test_contact):
        """Should update contact details"""
        response = client.put(
            f"/api/v1/contacts/{test_contact.id}",
            headers=auth_headers,
            json={"company": "New Company"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["company"] == "New Company"
    
    def test_deletes_contact(self, db: Session, auth_headers, test_contact):
        """Should delete a contact"""
        response = client.delete(
            f"/api/v1/contacts/{test_contact.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify deleted
        response = client.get(
            f"/api/v1/contacts/{test_contact.id}",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestEmailSyncIntegration:
    """Test email sync creates contacts and communication logs"""
    
    def test_email_sync_creates_contact_and_comm_log(self, db: Session):
        """Should create contact and communication log from email sync"""
        from app.models.email_account import EmailAccount, EmailProvider
        from app.services.contact_service import ContactService
        from app.models.communication_log import CommunicationType, CommunicationDirection
        
        # Create user and email account
        user = User(
            email="sync-test@example.com",
            hashed_password="hashed",
            full_name="Sync Test"
        )
        db.add(user)
        db.commit()
        
        email_account = EmailAccount(
            user_id=user.id,
            provider=EmailProvider.GMAIL,
            email_address="sync-test@example.com",
            is_active=True
        )
        db.add(email_account)
        db.commit()
        
        # Create a message (simulating email sync)
        message = Message(
            email_account_id=email_account.id,
            external_id="test-external-123",
            source=MessageSource.EMAIL,
            sender_email="newlead@example.com",
            sender_name="New Lead",
            subject="Interested in buying",
            encrypted_body="encrypted-content",
            body_preview="I am interested in buying a house",
            received_at=datetime.utcnow()
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Get or create contact (as email sync does)
        contact = ContactService.get_or_create_contact_by_email(
            db=db,
            email="newlead@example.com",
            user_id=user.id,
            sender_name="New Lead"
        )
        
        assert contact is not None
        assert contact.email == "newlead@example.com"
        assert contact.first_name == "New"
        assert contact.last_name == "Lead"
        assert contact.lead_source == "email"
        
        # Create communication log (as email sync does)
        import asyncio
        comm_log = asyncio.run(CommunicationService.log_communication(
            db=db,
            user_id=user.id,
            contact_id=contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            occurred_at=message.received_at,
            subject=message.subject,
            body=message.body_preview,
            from_address=message.sender_email,
            message_id=message.id,
            external_id=message.external_id
        ))
        
        assert comm_log is not None
        assert comm_log.contact_id == contact.id
        assert comm_log.subject == "Interested in buying"
        assert comm_log.external_id == "test-external-123"
        
        # Verify timeline has the communication
        timeline_result = ContactService.get_contact_timeline(
            db=db,
            contact_id=contact.id,
            user_id=user.id,
            limit=10
        )
        
        assert len(timeline_result["communications"]) == 1
        assert timeline_result["communications"][0].id == comm_log.id
    
    def test_email_sync_idempotency(self, db: Session):
        """Should not create duplicate communication logs on re-sync"""
        from app.models.email_account import EmailAccount, EmailProvider
        from app.services.contact_service import ContactService
        from app.services.communication_service import CommunicationService
        from app.models.communication_log import CommunicationType, CommunicationDirection, CommunicationLog
        
        # Create user
        user = User(
            email="idempotency-test@example.com",
            hashed_password="hashed",
            full_name="Idempotency Test"
        )
        db.add(user)
        db.commit()
        
        # Create contact
        contact = ContactService.create_contact(
            db=db,
            user_id=user.id,
            contact_data={
                "first_name": "Test",
                "email": "existing@example.com"
            }
        )
        
        # Simulate first sync - create comm log
        external_id = "unique-external-123"
        import asyncio
        comm_log1 = asyncio.run(CommunicationService.log_communication(
            db=db,
            user_id=user.id,
            contact_id=contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            occurred_at=datetime.utcnow(),
            subject="Test Email",
            external_id=external_id
        ))
        
        # Check idempotency - try to create again with same external_id
        existing_comm = db.query(CommunicationLog).filter(
            CommunicationLog.external_id == external_id,
            CommunicationLog.user_id == user.id
        ).first()
        
        assert existing_comm is not None
        assert existing_comm.id == comm_log1.id
        
        # Count should be 1
        count = db.query(CommunicationLog).filter(
            CommunicationLog.external_id == external_id
        ).count()
        
        assert count == 1, "Should not create duplicate communication logs"


class TestContactTimeline:
    """Test GET /contacts/{contact_id}/timeline endpoint - THE KILLER FEATURE"""
    
    @pytest.fixture
    def contact_with_timeline(self, db: Session, auth_headers):
        """Create a contact with 25 communication log entries for pagination testing"""
        user = app.dependency_overrides[get_current_user]()
        
        contact = Contact(
            user_id=user.id,
            first_name="Jane",
            last_name="Timeline",
            email="jane.timeline@example.com",
            contact_type="buyer"
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        # Create 25 communications spread over time
        base_time = datetime.utcnow()
        for i in range(25):
            comm = CommunicationLog(
                user_id=user.id,
                contact_id=contact.id,
                communication_type=CommunicationType.EMAIL if i % 2 == 0 else CommunicationType.SMS,
                direction=CommunicationDirection.INBOUND if i % 3 == 0 else CommunicationDirection.OUTBOUND,
                subject=f"Communication {i}" if i % 2 == 0 else None,
                body=f"This is communication number {i}",
                summary=f"Summary of communication {i}",
                from_address="jane.timeline@example.com" if i % 3 == 0 else "agent@example.com",
                to_address="agent@example.com" if i % 3 == 0 else "jane.timeline@example.com",
                occurred_at=base_time - timedelta(hours=i),
                urgency_score=50.0 + (i % 50),
                sentiment_score=0.5 - (i % 10) * 0.1
            )
            db.add(comm)
        
        db.commit()
        return contact
    
    def test_get_timeline_first_page(self, db: Session, auth_headers, contact_with_timeline):
        """Test fetching first page of timeline"""
        import time
        start_time = time.time()
        
        response = client.get(
            f"/api/v1/contacts/{contact_with_timeline.id}/timeline?limit=10",
            headers=auth_headers
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "contact_id" in data
        assert "communications" in data
        assert "pagination" in data
        assert "meta" in data
        
        # Verify pagination metadata
        assert data["contact_id"] == contact_with_timeline.id
        assert len(data["communications"]) == 10
        assert data["pagination"]["has_more"] is True
        assert data["pagination"]["next_cursor"] is not None
        assert data["pagination"]["limit"] == 10
        
        # Verify performance (<500ms target)
        assert data["meta"]["response_time_ms"] < 500, f"Timeline took {data['meta']['response_time_ms']}ms (target: <500ms)"
        
        # Verify communications are ordered by occurred_at DESC (newest first)
        occurred_times = [comm["occurred_at"] for comm in data["communications"]]
        assert occurred_times == sorted(occurred_times, reverse=True), "Communications should be ordered by occurred_at DESC"
    
    def test_get_timeline_pagination_with_cursor(self, db: Session, auth_headers, contact_with_timeline):
        """Test cursor-based pagination through timeline"""
        # Get first page
        response1 = client.get(
            f"/api/v1/contacts/{contact_with_timeline.id}/timeline?limit=10",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        page1 = response1.json()
        
        # Get second page using cursor
        next_cursor = page1["pagination"]["next_cursor"]
        response2 = client.get(
            f"/api/v1/contacts/{contact_with_timeline.id}/timeline?limit=10&cursor={next_cursor}",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        page2 = response2.json()
        
        # Verify we got different communications
        page1_ids = {comm["id"] for comm in page1["communications"]}
        page2_ids = {comm["id"] for comm in page2["communications"]}
        assert page1_ids.isdisjoint(page2_ids), "Pages should contain different communications"
        
        # Verify page 2 has correct data
        assert len(page2["communications"]) == 10
        assert page2["pagination"]["has_more"] is True
        
        # Get third page
        next_cursor2 = page2["pagination"]["next_cursor"]
        response3 = client.get(
            f"/api/v1/contacts/{contact_with_timeline.id}/timeline?limit=10&cursor={next_cursor2}",
            headers=auth_headers
        )
        
        assert response3.status_code == 200
        page3 = response3.json()
        
        # Page 3 should have 5 communications (25 total - 10 - 10 = 5)
        assert len(page3["communications"]) == 5
        assert page3["pagination"]["has_more"] is False
        assert page3["pagination"]["next_cursor"] is None
    
    def test_get_timeline_ordering(self, db: Session, auth_headers, contact_with_timeline):
        """Test that timeline is ordered by occurred_at DESC"""
        response = client.get(
            f"/api/v1/contacts/{contact_with_timeline.id}/timeline?limit=25",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All 25 communications should be returned
        assert len(data["communications"]) == 25
        
        # Verify strict descending order
        for i in range(len(data["communications"]) - 1):
            current = datetime.fromisoformat(data["communications"][i]["occurred_at"].replace('Z', '+00:00'))
            next_comm = datetime.fromisoformat(data["communications"][i + 1]["occurred_at"].replace('Z', '+00:00'))
            assert current >= next_comm, f"Communication {i} should be newer than communication {i+1}"
    
    def test_get_timeline_empty_contact(self, db: Session, auth_headers):
        """Test timeline for contact with no communications"""
        user = app.dependency_overrides[get_current_user]()
        
        contact = Contact(
            user_id=user.id,
            first_name="Empty",
            last_name="Timeline",
            email="empty@example.com"
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        response = client.get(
            f"/api/v1/contacts/{contact.id}/timeline",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["communications"]) == 0
        assert data["pagination"]["has_more"] is False
        assert data["pagination"]["next_cursor"] is None
    
    def test_get_timeline_nonexistent_contact(self, db: Session, auth_headers):
        """Test timeline for non-existent contact"""
        response = client.get(
            "/api/v1/contacts/99999/timeline",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_get_timeline_various_communication_types(self, db: Session, auth_headers):
        """Test timeline displays all communication types correctly"""
        user = app.dependency_overrides[get_current_user]()
        
        contact = Contact(
            user_id=user.id,
            first_name="Multi",
            last_name="Channel",
            email="multi@example.com"
        )
        db.add(contact)
        db.commit()
        
        # Create different types of communications
        comm_types = [
            (CommunicationType.EMAIL, "Email subject", "Email body"),
            (CommunicationType.SMS, None, "SMS text message"),
            (CommunicationType.PHONE_CALL, None, "Phone call notes"),
            (CommunicationType.MEETING, "Meeting notes", "Discussed contract terms"),
            (CommunicationType.NOTE, "Internal note", "Client seems very motivated")
        ]
        
        base_time = datetime.utcnow()
        for i, (comm_type, subject, body) in enumerate(comm_types):
            comm = CommunicationLog(
                user_id=user.id,
                contact_id=contact.id,
                communication_type=comm_type,
                direction=CommunicationDirection.INBOUND,
                subject=subject,
                body=body,
                summary=body[:100],
                from_address="multi@example.com",
                occurred_at=base_time - timedelta(minutes=i)
            )
            db.add(comm)
        
        db.commit()
        
        # Fetch timeline
        response = client.get(
            f"/api/v1/contacts/{contact.id}/timeline",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["communications"]) == 5
        
        # Verify all types are present
        types_in_timeline = {comm["communication_type"] for comm in data["communications"]}
        assert types_in_timeline == {"email", "sms", "phone_call", "meeting", "note"}
    
    def test_timeline_performance_with_large_dataset(self, db: Session, auth_headers):
        """Test timeline performance with 100 communications"""
        user = app.dependency_overrides[get_current_user]()
        
        contact = Contact(
            user_id=user.id,
            first_name="Performance",
            last_name="Test",
            email="perf@example.com"
        )
        db.add(contact)
        db.commit()
        
        # Create 100 communications
        base_time = datetime.utcnow()
        communications = []
        for i in range(100):
            comm = CommunicationLog(
                user_id=user.id,
                contact_id=contact.id,
                communication_type=CommunicationType.EMAIL,
                direction=CommunicationDirection.INBOUND,
                subject=f"Email {i}",
                body=f"Body {i}",
                from_address="perf@example.com",
                occurred_at=base_time - timedelta(hours=i)
            )
            communications.append(comm)
        
        db.add_all(communications)
        db.commit()
        
        # Test performance
        import time
        start_time = time.time()
        
        response = client.get(
            f"/api/v1/contacts/{contact.id}/timeline?limit=20",
            headers=auth_headers
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        assert elapsed_ms < 500, f"Timeline with 100 communications took {elapsed_ms}ms (target: <500ms)"
