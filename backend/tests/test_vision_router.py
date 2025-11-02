"""Tests for VisionHome AI Router"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from io import BytesIO
import json

from app.main import app
from app.models.user import User, SubscriptionTier


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


@pytest.fixture
def authenticated_client(client, test_user, test_token):
    """Client with authentication"""
    client.headers.update({"Authorization": f"Bearer {test_token}"})
    return client


@pytest.fixture
def mock_vision_agent():
    """Mock VisionAgent"""
    with patch('app.routers.vision.VisionAgent') as mock:
        agent_instance = Mock()
        agent_instance.analyze_property_image = AsyncMock(return_value={
            'vision_analysis': {
                'labels': [{'description': 'Kitchen', 'score': 0.95}],
                'objects': [{'name': 'Refrigerator', 'score': 0.9}]
            },
            'llm_interpretation': {
                'property_type': 'single_family_home',
                'property_style': 'modern',
                'condition_score': 0.85,
                'key_features': ['large kitchen'],
                'renovation_suggestions': ['kitchen remodel'],
                'confidence_score': 0.88
            },
            'similar_properties': [
                {
                    'address': '123 Main St',
                    'price': 450000.0,
                    'bedrooms': 3,
                    'bathrooms': 2.5
                }
            ],
            'timestamp': '2024-01-01T00:00:00'
        })
        mock.return_value = agent_instance
        yield agent_instance


@pytest.fixture
def mock_check_tier_limit():
    """Mock tier limit check"""
    with patch('app.routers.vision.check_tier_limit') as mock:
        mock.return_value = None  # No exception = limit not exceeded
        yield mock


def test_analyze_property_image_success(authenticated_client, mock_vision_agent, mock_check_tier_limit):
    """Test successful property image analysis endpoint"""
    # Create fake image file
    image_data = b"fake_image_bytes"
    files = {
        'file': ('property.jpg', BytesIO(image_data), 'image/jpeg')
    }
    data = {
        'property_address': '123 Main St, Seattle, WA'
    }
    
    response = authenticated_client.post(
        "/api/v1/vision/analyze",
        files=files,
        data=data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert 'id' in data
    assert 'status' in data
    assert data['status'] == 'pending' or data['status'] == 'processing'


def test_analyze_property_image_no_file(authenticated_client, mock_check_tier_limit):
    """Test property image analysis without file"""
    response = authenticated_client.post(
        "/api/v1/vision/analyze",
        data={'property_address': '123 Main St'}
    )
    
    assert response.status_code == 422  # Validation error


def test_analyze_property_image_unauthenticated(client):
    """Test that unauthenticated requests are rejected"""
    files = {
        'file': ('property.jpg', BytesIO(b"fake"), 'image/jpeg')
    }
    
    response = client.post(
        "/api/v1/vision/analyze",
        files=files
    )
    
    assert response.status_code == 401


def test_analyze_property_image_tier_limit_exceeded(authenticated_client, mock_check_tier_limit):
    """Test that tier limit exceptions are handled"""
    from app.shared.exceptions import SubscriptionLimitException
    
    mock_check_tier_limit.side_effect = SubscriptionLimitException(
        "Limit reached",
        feature="vision_scans",
        limit=5,
        current_usage=5
    )
    
    files = {
        'file': ('property.jpg', BytesIO(b"fake"), 'image/jpeg')
    }
    
    response = authenticated_client.post(
        "/api/v1/vision/analyze",
        files=files
    )
    
    assert response.status_code == 403
    data = response.json()
    assert 'detail' in data
    assert 'limit' in data['detail']
    assert data['detail']['limit'] == 5


def test_get_vision_scan_not_found(authenticated_client):
    """Test getting non-existent vision scan"""
    response = authenticated_client.get("/api/v1/vision/scans/99999")
    
    assert response.status_code == 404


def test_list_vision_scans(authenticated_client, test_user):
    """Test listing user's vision scans"""
    from app.db import SessionLocal
    from app.models.vision_scan import VisionScan
    
    # Create a test scan
    db = SessionLocal()
    try:
        scan = VisionScan(
            user_id=test_user.id,
            image_url="https://example.com/image.jpg",
            status="completed"
        )
        db.add(scan)
        db.commit()
        scan_id = scan.id
        
        response = authenticated_client.get("/api/v1/vision/scans")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should contain our test scan
        scan_ids = [s['id'] for s in data]
        assert scan_id in scan_ids
    finally:
        db.close()


def test_get_vision_scan_details(authenticated_client, test_user):
    """Test getting vision scan details"""
    from app.db import SessionLocal
    from app.models.vision_scan import VisionScan
    
    db = SessionLocal()
    try:
        scan = VisionScan(
            user_id=test_user.id,
            image_url="https://example.com/image.jpg",
            status="completed",
            matches=[{"address": "123 Main St", "price": 450000}],
            renovations={"kitchen": "remodel"},
            property_type="single_family_home"
        )
        db.add(scan)
        db.commit()
        scan_id = scan.id
        
        response = authenticated_client.get(f"/api/v1/vision/scans/{scan_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == scan_id
        assert data['status'] == 'completed'
        assert 'matches' in data
        assert 'renovations' in data
    finally:
        db.close()


def test_get_vision_scan_unauthorized(authenticated_client, test_user):
    """Test that users can't access other users' scans"""
    from app.db import SessionLocal
    from app.models.vision_scan import VisionScan
    from app.models.user import User
    
    # Create another user
    db = SessionLocal()
    try:
        other_user = User(
            email="other@example.com",
            password_hash="hash",
            full_name="Other User",
            subscription_tier=SubscriptionTier.FREE_TRIAL
        )
        db.add(other_user)
        db.commit()
        
        # Create scan for other user
        scan = VisionScan(
            user_id=other_user.id,
            image_url="https://example.com/image.jpg",
            status="completed"
        )
        db.add(scan)
        db.commit()
        scan_id = scan.id
        
        # Try to access with test_user
        response = authenticated_client.get(f"/api/v1/vision/scans/{scan_id}")
        
        assert response.status_code == 404  # Should not find (filtered by user)
    finally:
        db.close()

