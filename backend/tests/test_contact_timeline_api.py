"""
Contact Timeline API Tests
Tests the critical /contacts/{id}/timeline endpoint with cursor-based pagination
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import time

from app.models.contact import Contact
from app.models.communication_log import CommunicationLog, CommunicationType, CommunicationDirection


class TestContactTimelineAPI:
    """Test the contact timeline endpoint"""
    
    @pytest.fixture
    def sample_contact(self, db: Session, test_user):
        """Create a sample contact for testing"""
        contact = Contact(
            user_id=test_user.id,
            first_name="John",
            last_name="Buyer",
            email="john.buyer@example.com",
            phone="555-1234",
            contact_type="buyer",
            contact_status="active"
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact
    
    def test_get_contact_timeline_empty(
        self,
        client: TestClient,
        auth_headers,
        test_user,
        sample_contact
    ):
        """Timeline returns empty array for contact with no communications"""
        response = client.get(
            f"/api/v1/contacts/{sample_contact.id}/timeline",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "communications" in data
        assert "pagination" in data
        assert len(data["communications"]) == 0
        assert data["pagination"]["has_more"] is False
        assert data["pagination"]["next_cursor"] is None
    
    def test_get_contact_timeline_with_communications(
        self,
        client: TestClient,
        auth_headers,
        test_user,
        sample_contact,
        db: Session
    ):
        """Timeline returns communications in DESC order with pagination"""
        # Create 3 communications with different timestamps
        now = datetime.utcnow()
        
        comm1 = CommunicationLog(
            user_id=test_user.id,
            contact_id=sample_contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            subject="First email",
            body="This is the oldest email",
            from_address="john.buyer@example.com",
            occurred_at=now - timedelta(hours=48)  # 2 days ago
        )
        
        comm2 = CommunicationLog(
            user_id=test_user.id,
            contact_id=sample_contact.id,
            communication_type=CommunicationType.SMS,
            direction=CommunicationDirection.OUTBOUND,
            subject=None,
            body="Quick text response",
            from_address=test_user.email,
            occurred_at=now - timedelta(hours=24)  # 1 day ago
        )
        
        comm3 = CommunicationLog(
            user_id=test_user.id,
            contact_id=sample_contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            subject="Latest email",
            body="This is the most recent email",
            from_address="john.buyer@example.com",
            occurred_at=now - timedelta(hours=1)  # 1 hour ago (most recent)
        )
        
        db.add_all([comm1, comm2, comm3])
        db.commit()
        
        # Request first page with limit=2
        response = client.get(
            f"/api/v1/contacts/{sample_contact.id}/timeline?limit=2",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return 2 most recent communications
        assert len(data["communications"]) == 2
        assert data["pagination"]["has_more"] is True
        assert data["pagination"]["next_cursor"] is not None
        
        # Verify order (most recent first)
        assert data["communications"][0]["subject"] == "Latest email"
        assert data["communications"][1]["subject"] is None  # SMS has no subject
        
        # Request second page using cursor
        cursor = data["pagination"]["next_cursor"]
        response2 = client.get(
            f"/api/v1/contacts/{sample_contact.id}/timeline?cursor={cursor}&limit=2",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should return the 3rd (oldest) communication
        assert len(data2["communications"]) == 1
        assert data2["pagination"]["has_more"] is False
        assert data2["pagination"]["next_cursor"] is None
        assert data2["communications"][0]["subject"] == "First email"
    
    def test_contact_timeline_performance(
        self,
        client: TestClient,
        auth_headers,
        test_user,
        sample_contact,
        db: Session
    ):
        """Timeline response time < 500ms even with many communications"""
        # Create 100 communications
        now = datetime.utcnow()
        communications = []
        
        for i in range(100):
            comm = CommunicationLog(
                user_id=test_user.id,
                contact_id=sample_contact.id,
                communication_type=CommunicationType.EMAIL if i % 2 == 0 else CommunicationType.SMS,
                direction=CommunicationDirection.INBOUND if i % 3 == 0 else CommunicationDirection.OUTBOUND,
                subject=f"Communication {i}" if i % 2 == 0 else None,
                body=f"This is communication number {i}",
                summary=f"Summary of communication {i}",
                from_address="john.buyer@example.com",
                occurred_at=now - timedelta(hours=i),  # Spread over time
                sentiment_score=0.5 if i % 4 == 0 else None,
                urgency_score=50.0 if i % 5 == 0 else None
            )
            communications.append(comm)
        
        db.add_all(communications)
        db.commit()
        
        # Measure response time
        start_time = time.time()
        response = client.get(
            f"/api/v1/contacts/{sample_contact.id}/timeline?limit=20",
            headers=auth_headers
        )
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify performance
        assert elapsed_ms < 500, f"Response took {elapsed_ms:.2f}ms, expected < 500ms"
        
        # Verify pagination works
        assert len(data["communications"]) == 20
        assert data["pagination"]["has_more"] is True
        
        # Verify response includes performance metadata
        assert "meta" in data
        assert "response_time_ms" in data["meta"]
    
    def test_timeline_with_different_communication_types(
        self,
        client: TestClient,
        auth_headers,
        test_user,
        sample_contact,
        db: Session
    ):
        """Timeline properly displays all communication types"""
        now = datetime.utcnow()
        
        # Create various communication types
        email = CommunicationLog(
            user_id=test_user.id,
            contact_id=sample_contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            subject="Email subject",
            body="Email body",
            from_address="john@example.com",
            occurred_at=now - timedelta(hours=5)
        )
        
        sms = CommunicationLog(
            user_id=test_user.id,
            contact_id=sample_contact.id,
            communication_type=CommunicationType.SMS,
            direction=CommunicationDirection.OUTBOUND,
            body="Text message",
            from_address=test_user.email,
            occurred_at=now - timedelta(hours=4)
        )
        
        phone_call = CommunicationLog(
            user_id=test_user.id,
            contact_id=sample_contact.id,
            communication_type=CommunicationType.PHONE_CALL,
            direction=CommunicationDirection.OUTBOUND,
            body="Discussed property details",
            duration_seconds=600,  # 10 minute call
            from_address=test_user.email,
            occurred_at=now - timedelta(hours=3)
        )
        
        meeting = CommunicationLog(
            user_id=test_user.id,
            contact_id=sample_contact.id,
            communication_type=CommunicationType.MEETING,
            direction=CommunicationDirection.INTERNAL,
            subject="Property showing",
            body="Showed 123 Main St",
            duration_seconds=3600,  # 1 hour meeting
            occurred_at=now - timedelta(hours=2)
        )
        
        note = CommunicationLog(
            user_id=test_user.id,
            contact_id=sample_contact.id,
            communication_type=CommunicationType.NOTE,
            direction=CommunicationDirection.INTERNAL,
            body="Client seems very interested, pre-approved for $500k",
            occurred_at=now - timedelta(hours=1)
        )
        
        db.add_all([email, sms, phone_call, meeting, note])
        db.commit()
        
        # Fetch timeline
        response = client.get(
            f"/api/v1/contacts/{sample_contact.id}/timeline",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["communications"]) == 5
        
        # Verify all types are represented
        types = [comm["communication_type"] for comm in data["communications"]]
        assert "email" in types
        assert "sms" in types
        assert "phone_call" in types
        assert "meeting" in types
        assert "note" in types
    
    def test_timeline_contact_not_found(
        self,
        client: TestClient,
        auth_headers
    ):
        """Timeline returns 404 for non-existent contact"""
        response = client.get(
            "/api/v1/contacts/99999/timeline",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_timeline_unauthorized(
        self,
        client: TestClient,
        sample_contact
    ):
        """Timeline requires authentication"""
        response = client.get(
            f"/api/v1/contacts/{sample_contact.id}/timeline"
        )
        
        assert response.status_code == 401
    
    def test_timeline_pagination_cursor_format(
        self,
        client: TestClient,
        auth_headers,
        test_user,
        sample_contact,
        db: Session
    ):
        """Cursor is properly formatted as timestamp:id"""
        now = datetime.utcnow()
        
        comm1 = CommunicationLog(
            user_id=test_user.id,
            contact_id=sample_contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            body="Test 1",
            from_address="test@example.com",
            occurred_at=now - timedelta(hours=2)
        )
        
        comm2 = CommunicationLog(
            user_id=test_user.id,
            contact_id=sample_contact.id,
            communication_type=CommunicationType.EMAIL,
            direction=CommunicationDirection.INBOUND,
            body="Test 2",
            from_address="test@example.com",
            occurred_at=now - timedelta(hours=1)
        )
        
        db.add_all([comm1, comm2])
        db.commit()
        
        response = client.get(
            f"/api/v1/contacts/{sample_contact.id}/timeline?limit=1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        cursor = data["pagination"]["next_cursor"]
        assert cursor is not None
        
        # Cursor should be in format "timestamp:id"
        assert ":" in cursor
        parts = cursor.split(":")
        assert len(parts) == 2
        
        # First part should be ISO timestamp
        try:
            datetime.fromisoformat(parts[0])
        except ValueError:
            pytest.fail(f"Cursor timestamp part '{parts[0]}' is not valid ISO format")
        
        # Second part should be integer ID
        assert parts[1].isdigit()

