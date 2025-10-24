"""
CSV Contact Import Tests
Tests the CSV import functionality with field mapping and duplicate detection
"""
import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.contact import Contact
from app.dependencies import get_current_user


client = TestClient(app)


@pytest.fixture
def auth_headers(db: Session):
    """Create authenticated user and return auth headers"""
    user = User(
        email="import@example.com",
        hashed_password="hashed",
        full_name="Import Tester"
    )
    db.add(user)
    db.commit()
    
    def override_get_current_user():
        return user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    yield {"Authorization": "Bearer fake-token"}, user
    
    app.dependency_overrides.clear()


class TestCSVImport:
    """Test CSV import functionality"""
    
    def create_csv_file(self, rows):
        """Helper to create CSV file from rows"""
        import csv
        
        output = io.StringIO()
        if rows:
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        
        output.seek(0)
        return output.getvalue().encode('utf-8')
    
    def test_import_basic_contacts(self, db: Session, auth_headers):
        """Test importing basic contact CSV with 10 contacts"""
        headers, user = auth_headers
        
        # Create CSV with 10 contacts
        csv_data = [
            {
                "First Name": "Alice",
                "Last Name": "Anderson",
                "Email": "alice@example.com",
                "Phone": "555-0001",
                "Type": "buyer"
            },
            {
                "First Name": "Bob",
                "Last Name": "Brown",
                "Email": "bob@example.com",
                "Phone": "555-0002",
                "Type": "seller"
            },
            {
                "First Name": "Carol",
                "Last Name": "Clark",
                "Email": "carol@example.com",
                "Phone": "555-0003",
                "Type": "lead"
            },
            {
                "First Name": "David",
                "Last Name": "Davis",
                "Email": "david@example.com",
                "Phone": "555-0004",
                "Type": "buyer"
            },
            {
                "First Name": "Eve",
                "Last Name": "Evans",
                "Email": "eve@example.com",
                "Phone": "555-0005",
                "Type": "seller"
            },
            {
                "First Name": "Frank",
                "Last Name": "Foster",
                "Email": "frank@example.com",
                "Phone": "555-0006",
                "Type": "lead"
            },
            {
                "First Name": "Grace",
                "Last Name": "Green",
                "Email": "grace@example.com",
                "Phone": "555-0007",
                "Type": "buyer"
            },
            {
                "First Name": "Henry",
                "Last Name": "Hill",
                "Email": "henry@example.com",
                "Phone": "555-0008",
                "Type": "agent"
            },
            {
                "First Name": "Iris",
                "Last Name": "Irwin",
                "Email": "iris@example.com",
                "Phone": "555-0009",
                "Type": "vendor"
            },
            {
                "First Name": "Jack",
                "Last Name": "Jones",
                "Email": "jack@example.com",
                "Phone": "555-0010",
                "Type": "buyer"
            }
        ]
        
        csv_content = self.create_csv_file(csv_data)
        
        # Field mapping
        field_mapping = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "phone": "Phone",
            "contact_type": "Type"
        }
        
        # Import
        response = client.post(
            "/api/v1/contacts/import",
            headers=headers,
            files={"file": ("contacts.csv", csv_content, "text/csv")},
            params={
                "field_mapping": str(field_mapping).replace("'", '"'),
                "duplicate_strategy": "skip"
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify import results
        assert result["created"] == 10
        assert result["skipped"] == 0
        assert result["failed"] == 0
        
        # Verify contacts in database
        contacts = db.query(Contact).filter(Contact.user_id == user.id).all()
        assert len(contacts) == 10
        
        # Verify specific contacts
        alice = db.query(Contact).filter(
            Contact.user_id == user.id,
            Contact.email == "alice@example.com"
        ).first()
        assert alice is not None
        assert alice.first_name == "Alice"
        assert alice.last_name == "Anderson"
        assert alice.phone == "555-0001"
        assert alice.contact_type == "buyer"
        
        # Verify all emails are unique and correct
        emails = {c.email for c in contacts}
        assert len(emails) == 10
        assert "alice@example.com" in emails
        assert "jack@example.com" in emails
    
    def test_import_duplicate_detection_skip(self, db: Session, auth_headers):
        """Test duplicate detection with 'skip' strategy"""
        headers, user = auth_headers
        
        # Create initial CSV
        csv_data = [
            {
                "First Name": "John",
                "Last Name": "Doe",
                "Email": "john@example.com",
                "Phone": "555-1111"
            },
            {
                "First Name": "Jane",
                "Last Name": "Smith",
                "Email": "jane@example.com",
                "Phone": "555-2222"
            }
        ]
        
        csv_content = self.create_csv_file(csv_data)
        
        field_mapping = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "phone": "Phone"
        }
        
        # First import
        response1 = client.post(
            "/api/v1/contacts/import",
            headers=headers,
            files={"file": ("contacts.csv", csv_content, "text/csv")},
            params={
                "field_mapping": str(field_mapping).replace("'", '"'),
                "duplicate_strategy": "skip"
            }
        )
        
        assert response1.status_code == 200
        result1 = response1.json()
        assert result1["created"] == 2
        
        # Second import with same data
        response2 = client.post(
            "/api/v1/contacts/import",
            headers=headers,
            files={"file": ("contacts.csv", csv_content, "text/csv")},
            params={
                "field_mapping": str(field_mapping).replace("'", '"'),
                "duplicate_strategy": "skip"
            }
        )
        
        assert response2.status_code == 200
        result2 = response2.json()
        assert result2["created"] == 0
        assert result2["skipped"] == 2  # Both should be skipped
        
        # Verify only 2 contacts in database (no duplicates)
        contact_count = db.query(Contact).filter(Contact.user_id == user.id).count()
        assert contact_count == 2
    
    def test_import_duplicate_detection_update(self, db: Session, auth_headers):
        """Test duplicate detection with 'update' strategy"""
        headers, user = auth_headers
        
        # Create initial contact
        existing = Contact(
            user_id=user.id,
            first_name="Old",
            last_name="Name",
            email="update@example.com",
            phone="555-0000"
        )
        db.add(existing)
        db.commit()
        existing_id = existing.id
        
        # Import CSV with updated info
        csv_data = [
            {
                "First Name": "Updated",
                "Last Name": "Contact",
                "Email": "update@example.com",
                "Phone": "555-9999"
            }
        ]
        
        csv_content = self.create_csv_file(csv_data)
        
        field_mapping = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "phone": "Phone"
        }
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=headers,
            files={"file": ("contacts.csv", csv_content, "text/csv")},
            params={
                "field_mapping": str(field_mapping).replace("'", '"'),
                "duplicate_strategy": "update"
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["updated"] == 1
        assert result["created"] == 0
        
        # Verify contact was updated, not duplicated
        contact_count = db.query(Contact).filter(
            Contact.user_id == user.id,
            Contact.email == "update@example.com"
        ).count()
        assert contact_count == 1
        
        # Verify the update
        db.refresh(existing)
        assert existing.first_name == "Updated"
        assert existing.last_name == "Contact"
        assert existing.phone == "555-9999"
        assert existing.id == existing_id  # Same ID
    
    def test_import_with_company_and_address(self, db: Session, auth_headers):
        """Test importing contacts with additional fields"""
        headers, user = auth_headers
        
        csv_data = [
            {
                "First": "Commercial",
                "Last": "Client",
                "Email": "commercial@realty.com",
                "Phone": "555-8888",
                "Company": "Big Realty Corp",
                "City": "New York",
                "State": "NY",
                "ZIP": "10001"
            }
        ]
        
        csv_content = self.create_csv_file(csv_data)
        
        field_mapping = {
            "first_name": "First",
            "last_name": "Last",
            "email": "Email",
            "phone": "Phone",
            "company": "Company",
            "city": "City",
            "state": "State",
            "zip_code": "ZIP"
        }
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=headers,
            files={"file": ("contacts.csv", csv_content, "text/csv")},
            params={
                "field_mapping": str(field_mapping).replace("'", '"'),
                "duplicate_strategy": "skip"
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["created"] == 1
        
        # Verify contact details
        contact = db.query(Contact).filter(
            Contact.user_id == user.id,
            Contact.email == "commercial@realty.com"
        ).first()
        
        assert contact is not None
        assert contact.company == "Big Realty Corp"
        assert contact.city == "New York"
        assert contact.state == "NY"
        assert contact.zip_code == "10001"
    
    def test_import_invalid_csv_format(self, db: Session, auth_headers):
        """Test that invalid CSV format is rejected"""
        headers, user = auth_headers
        
        # Invalid CSV content
        invalid_content = b"Not a valid CSV format { broken data"
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=headers,
            files={"file": ("invalid.csv", invalid_content, "text/csv")},
            params={
                "field_mapping": '{"first_name": "First"}',
                "duplicate_strategy": "skip"
            }
        )
        
        # Should fail with appropriate error
        assert response.status_code in [400, 500]
    
    def test_import_file_size_limit(self, db: Session, auth_headers):
        """Test that files larger than 10MB are rejected"""
        headers, user = auth_headers
        
        # Create a file that's too large (> 10MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11 MB
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=headers,
            files={"file": ("large.csv", large_content, "text/csv")},
            params={
                "field_mapping": '{"first_name": "First"}',
                "duplicate_strategy": "skip"
            }
        )
        
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()
    
    def test_import_non_csv_file(self, db: Session, auth_headers):
        """Test that non-CSV files are rejected"""
        headers, user = auth_headers
        
        # Try to upload a text file
        response = client.post(
            "/api/v1/contacts/import",
            headers=headers,
            files={"file": ("document.txt", b"This is not a CSV", "text/plain")},
            params={
                "field_mapping": '{"first_name": "First"}',
                "duplicate_strategy": "skip"
            }
        )
        
        assert response.status_code == 400
        assert "csv" in response.json()["detail"].lower()
    
    def test_import_with_missing_required_fields(self, db: Session, auth_headers):
        """Test importing contacts with missing required fields"""
        headers, user = auth_headers
        
        # CSV missing first_name for one row
        csv_data = [
            {
                "First Name": "Valid",
                "Last Name": "Contact",
                "Email": "valid@example.com"
            },
            {
                "First Name": "",  # Missing required first_name
                "Last Name": "Invalid",
                "Email": "invalid@example.com"
            }
        ]
        
        csv_content = self.create_csv_file(csv_data)
        
        field_mapping = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email"
        }
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=headers,
            files={"file": ("contacts.csv", csv_content, "text/csv")},
            params={
                "field_mapping": str(field_mapping).replace("'", '"'),
                "duplicate_strategy": "skip"
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should create the valid one and report the failed one
        assert result["created"] == 1
        assert result["failed"] == 1
        assert "errors" in result
    
    def test_import_preserves_lead_source(self, db: Session, auth_headers):
        """Test that imported contacts have correct lead_source"""
        headers, user = auth_headers
        
        csv_data = [
            {
                "Name": "Import Test",
                "Email": "source@example.com"
            }
        ]
        
        csv_content = self.create_csv_file(csv_data)
        
        field_mapping = {
            "first_name": "Name",
            "email": "Email"
        }
        
        response = client.post(
            "/api/v1/contacts/import",
            headers=headers,
            files={"file": ("contacts.csv", csv_content, "text/csv")},
            params={
                "field_mapping": str(field_mapping).replace("'", '"'),
                "duplicate_strategy": "skip"
            }
        )
        
        assert response.status_code == 200
        
        # Verify lead_source is set to 'import'
        contact = db.query(Contact).filter(
            Contact.user_id == user.id,
            Contact.email == "source@example.com"
        ).first()
        
        assert contact is not None
        assert contact.lead_source == "import"

