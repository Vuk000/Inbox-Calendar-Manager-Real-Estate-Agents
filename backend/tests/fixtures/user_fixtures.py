"""
User and authentication test fixtures
"""
import pytest
from typing import Dict, Any
from datetime import datetime


@pytest.fixture
def test_user() -> Dict[str, Any]:
    """Standard test user"""
    return {
        "id": 1,
        "email": "agent@example.com",
        "full_name": "Test Agent",
        "role": "agent",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "subscription_tier": "professional"
    }


@pytest.fixture
def admin_user() -> Dict[str, Any]:
    """Admin test user"""
    return {
        "id": 2,
        "email": "admin@realinbox.ai",
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "subscription_tier": "enterprise"
    }


@pytest.fixture
def free_tier_user() -> Dict[str, Any]:
    """Free tier user"""
    return {
        "id": 3,
        "email": "free@example.com",
        "full_name": "Free User",
        "role": "agent",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "subscription_tier": "solo"
    }


@pytest.fixture
def test_email_account() -> Dict[str, Any]:
    """Test email account integration"""
    return {
        "id": 1,
        "user_id": 1,
        "email": "agent@example.com",
        "provider": "gmail",
        "is_active": True,
        "last_sync": datetime.utcnow(),
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token"
    }


@pytest.fixture
def mock_jwt_token() -> str:
    """Mock JWT token"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZ2VudEBleGFtcGxlLmNvbSIsInJvbGUiOiJhZ2VudCJ9.test_signature"


@pytest.fixture
def auth_headers(mock_jwt_token) -> Dict[str, str]:
    """Authorization headers"""
    return {"Authorization": f"Bearer {mock_jwt_token}"}

