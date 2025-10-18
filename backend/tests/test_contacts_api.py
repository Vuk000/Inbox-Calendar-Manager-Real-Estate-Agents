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

