"""
Tests for email API endpoints
"""
import pytest
from app.models.email_account import EmailAccount, EmailProvider
from app.models.message import Message, MessagePriority, MessageCategory, MessageSource
from app.models.social_account import SocialAccount, SocialProvider
from app.security.encryption import encrypt_data
from datetime import datetime


def test_list_emails_empty(client, auth_headers, test_user):
    """Test listing emails when user has no emails"""
    response = client.get(
        "/api/v1/emails",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_emails_with_data(client, auth_headers, test_user, db):
    """Test listing emails with data"""
    # Create email account
    account = EmailAccount(
        user_id=test_user.id,
        provider=EmailProvider.GMAIL,
        email_address="test@gmail.com",
        encrypted_access_token=encrypt_data("fake_token"),
        is_active=True
    )
    db.add(account)
    db.commit()
    
    # Create test messages
    message1 = Message(
        email_account_id=account.id,
        external_id="msg1",
        thread_id="thread1",
        source=MessageSource.EMAIL,
        sender_email="client@example.com",
        subject="Urgent: Offer expires today",
        encrypted_body=encrypt_data("This is urgent"),
        body_preview="This is urgent",
        priority=MessagePriority.HIGH,
        category=MessageCategory.OFFER,
        urgency_score=95.0,
        received_at=datetime.utcnow()
    )
    
    message2 = Message(
        email_account_id=account.id,
        external_id="msg2",
        thread_id="thread2",
        source=MessageSource.EMAIL,
        sender_email="lead@example.com",
        subject="Interested in viewing properties",
        encrypted_body=encrypt_data("I want to see properties"),
        body_preview="I want to see properties",
        priority=MessagePriority.MEDIUM,
        category=MessageCategory.LEAD,
        urgency_score=60.0,
        received_at=datetime.utcnow()
    )
    
    db.add(message1)
    db.add(message2)
    db.commit()
    
    # List all emails
    response = client.get(
        "/api/v1/emails",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Should be sorted by urgency (highest first)
    assert data[0]["urgency_score"] > data[1]["urgency_score"]


def test_list_emails_filter_by_priority(client, auth_headers, test_user, db):
    """Test filtering emails by priority"""
    # Setup data (similar to above)
    account = EmailAccount(
        user_id=test_user.id,
        provider=EmailProvider.GMAIL,
        email_address="test@gmail.com",
        encrypted_access_token=encrypt_data("fake_token"),
        is_active=True
    )
    db.add(account)
    db.commit()
    
    # Create high priority message
    message = Message(
        email_account_id=account.id,
        external_id="msg_high",
        thread_id="thread_high",
        source=MessageSource.EMAIL,
        sender_email="urgent@example.com",
        subject="Urgent matter",
        encrypted_body=encrypt_data("Urgent"),
        body_preview="Urgent",
        priority=MessagePriority.HIGH,
        category=MessageCategory.OFFER,
        urgency_score=90.0,
        received_at=datetime.utcnow()
    )
    db.add(message)
    db.commit()
    
    # Filter by high priority
    response = client.get(
        "/api/v1/emails?priority=high",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == "high"


def test_get_email_detail(client, auth_headers, test_user, db):
    """Test getting email details"""
    # Create account and message
    account = EmailAccount(
        user_id=test_user.id,
        provider=EmailProvider.GMAIL,
        email_address="test@gmail.com",
        encrypted_access_token=encrypt_data("fake_token"),
        is_active=True
    )
    db.add(account)
    db.commit()
    
    message = Message(
        email_account_id=account.id,
        external_id="msg_detail",
        thread_id="thread_detail",
        source=MessageSource.EMAIL,
        sender_email="detail@example.com",
        subject="Test Email",
        encrypted_body=encrypt_data("This is the full email body with details."),
        body_preview="This is the full email body",
        priority=MessagePriority.MEDIUM,
        category=MessageCategory.GENERAL,
        urgency_score=50.0,
        received_at=datetime.utcnow(),
        is_read=False
    )
    db.add(message)
    db.commit()
    
    # Get email detail
    response = client.get(
        f"/api/v1/emails/{message.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check detailed fields
    assert data["id"] == message.id
    assert data["subject"] == "Test Email"
    assert data["body"] == "This is the full email body with details."  # Decrypted
    assert "entities" in data
    assert "suggested_actions" in data


def test_email_stats(client, auth_headers, test_user, db):
    """Test email statistics endpoint"""
    # Create account and messages
    account = EmailAccount(
        user_id=test_user.id,
        provider=EmailProvider.GMAIL,
        email_address="test@gmail.com",
        encrypted_access_token=encrypt_data("fake_token"),
        is_active=True
    )
    db.add(account)
    db.commit()
    
    # Create 3 messages with different priorities
    for i in range(3):
        priority = MessagePriority.HIGH if i == 0 else MessagePriority.MEDIUM
        message = Message(
            email_account_id=account.id,
            external_id=f"msg_{i}",
            thread_id=f"thread_{i}",
            source=MessageSource.EMAIL,
            sender_email=f"sender{i}@example.com",
            subject=f"Email {i}",
            encrypted_body=encrypt_data(f"Body {i}"),
            body_preview=f"Body {i}",
            priority=priority,
            category=MessageCategory.GENERAL,
            urgency_score=90.0 - (i * 20),
            received_at=datetime.utcnow(),
            is_read=(i > 0)  # First is unread
        )
        db.add(message)
    
    db.commit()
    
    # Get stats
    response = client.get(
        "/api/v1/emails/stats/summary",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 3
    assert data["unread"] == 1
    assert data["urgent"] == 1  # One high priority


def test_list_emails_filter_social(client, auth_headers, test_user, db):
    """Ensure social inbox filter returns social messages only."""
    email_account = EmailAccount(
        user_id=test_user.id,
        provider=EmailProvider.GMAIL,
        email_address="test@gmail.com",
        encrypted_access_token=encrypt_data("token"),
        is_active=True
    )
    social_account = SocialAccount(
        user_id=test_user.id,
        provider=SocialProvider.TWITTER,
        handle="agent_realinbox",
        encrypted_access_token="token",
        is_active=True
    )
    db.add(email_account)
    db.add(social_account)
    db.commit()

    email_message = Message(
        email_account_id=email_account.id,
        external_id="email_1",
        thread_id="thread1",
        source=MessageSource.EMAIL,
        sender_email="buyer@example.com",
        subject="Email message",
        encrypted_body=encrypt_data("Email body"),
        body_preview="Email body",
        priority=MessagePriority.LOW,
        category=MessageCategory.GENERAL,
        urgency_score=10,
        received_at=datetime.utcnow()
    )
    social_message = Message(
        social_account_id=social_account.id,
        external_id="dm_1",
        thread_id="thread2",
        source=MessageSource.TWITTER_DM,
        sender_email="dm_user",
        subject="Twitter DM",
        encrypted_body=encrypt_data("DM body"),
        body_preview="DM body",
        priority=MessagePriority.MEDIUM,
        category=MessageCategory.LEAD,
        urgency_score=80,
        received_at=datetime.utcnow()
    )
    db.add_all([email_message, social_message])
    db.commit()

    response = client.get(
        "/api/v1/emails?source=social",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["source"] == MessageSource.TWITTER_DM.value


def test_search_emails(client, auth_headers, test_user, db):
    account = EmailAccount(
        user_id=test_user.id,
        provider=EmailProvider.GMAIL,
        email_address="agent@example.com",
        encrypted_access_token=encrypt_data("token"),
        is_active=True
    )
    db.add(account)
    db.commit()

    message = Message(
        email_account_id=account.id,
        external_id="search_1",
        thread_id="thread1",
        source=MessageSource.EMAIL,
        sender_email="lead@example.com",
        sender_name="Jane Buyer",
        subject="Showing request for 123 Main",
        encrypted_body=encrypt_data("Can we schedule a showing for 123 Main St?"),
        body_preview="Can we schedule a showing for 123 Main St?",
        priority=MessagePriority.MEDIUM,
        category=MessageCategory.SHOWING_REQUEST,
        urgency_score=65,
        received_at=datetime.utcnow()
    )
    db.add(message)
    db.commit()

    response = client.post(
        "/api/v1/emails/search",
        headers=auth_headers,
        json={"query": "123 Main"}
    )
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["subject"] == "Showing request for 123 Main"

