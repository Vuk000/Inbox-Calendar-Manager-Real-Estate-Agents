"""
Tests for authentication endpoints - Enhanced with comprehensive coverage
"""
import pytest
from datetime import datetime


@pytest.mark.unit
@pytest.mark.db
def test_register_new_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepass123",
            "full_name": "New Agent",
            "phone_number": "+1-555-0123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["full_name"] == "New Agent"
    assert data["user"]["role"] == "agent"
    assert data["user"]["subscription_tier"] == "free_trial"


@pytest.mark.unit
@pytest.mark.db
def test_register_password_too_short(client):
    """Test that password validation works"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "short",  # Too short
            "full_name": "New Agent"
        }
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
@pytest.mark.db
def test_register_duplicate_email(client, test_user):
    """Test that duplicate email registration fails"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "password123",
            "full_name": "Duplicate User"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.unit
@pytest.mark.db
def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["subscription_tier"] == "pro_agent"


@pytest.mark.unit
@pytest.mark.db
def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.unit
@pytest.mark.db
def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.db
def test_login_inactive_account(client, db, test_user):
    """Test login with inactive account"""
    test_user.is_active = False
    db.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 403


@pytest.mark.unit
@pytest.mark.db
def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test Agent"
    assert "subscription_tier" in data
    assert "role" in data
    assert "ai_actions_used" in data
    assert "ai_actions_limit" in data


@pytest.mark.unit
@pytest.mark.db
def test_refresh_token(client, test_user):
    """Test token refresh"""
    # First login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    # New refresh token should be different
    assert data["refresh_token"] != refresh_token


@pytest.mark.unit
@pytest.mark.db
def test_refresh_token_invalid(client):
    """Test refresh with invalid token"""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-token"}
    )
    
    assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.db
def test_update_profile(client, auth_headers):
    """Test updating user profile"""
    response = client.patch(
        "/api/v1/auth/me",
        headers=auth_headers,
        json={
            "full_name": "Updated Name",
            "phone_number": "+1-555-9999"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["phone_number"] == "+1-555-9999"


@pytest.mark.unit
@pytest.mark.db
def test_change_password_success(client, auth_headers, test_user):
    """Test successful password change"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
    )
    
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify new password works
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "newpassword123"
        }
    )
    assert login_response.status_code == 200


@pytest.mark.unit
@pytest.mark.db
def test_change_password_wrong_current(client, auth_headers):
    """Test password change with wrong current password"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
    )
    
    assert response.status_code == 400
    assert "current password" in response.json()["detail"].lower()


@pytest.mark.unit
@pytest.mark.db
def test_change_password_too_short(client, auth_headers):
    """Test password change with too short new password"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "testpassword123",
            "new_password": "short"
        }
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without authentication token"""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.unit
def test_protected_endpoint_with_invalid_token(client):
    """Test accessing protected endpoint with invalid token"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token-12345"}
    )
    
    assert response.status_code == 401
