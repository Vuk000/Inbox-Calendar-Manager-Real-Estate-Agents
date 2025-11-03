"""Integration tests for API endpoints"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from io import BytesIO


@pytest.mark.integration
@pytest.mark.db
def test_vision_workflow(client, db, test_user):
    """Test complete vision scan workflow"""
    from app.models.user import User, SubscriptionTier
    from app.security.encryption import hash_password
    
    # Create authenticated user
    user = User(
        email="vision_test@example.com",
        hashed_password=hash_password("password123"),
        full_name="Vision Test User",
        subscription_tier=SubscriptionTier.PRO_AGENT,
        is_active=True,
        ai_actions_limit=1000
    )
    db.add(user)
    db.commit()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "vision_test@example.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create vision scan
    with patch('app.routers.vision.VisionAgent') as mock_vision:
        mock_agent = Mock()
        mock_agent.analyze_property_image = AsyncMock(return_value={
            'matches': [{'address': '123 Main St', 'price': 450000}],
            'renovations': {'kitchen': 'remodel'},
            'vision_labels': ['kitchen', 'living room'],
            'rooms_detected': ['kitchen', 'living room'],
            'analysis': {'property_type': 'house'}
        })
        mock_vision.return_value = mock_agent
        
        with patch('app.routers.vision.check_tier_limit'):
            files = {'file': ('property.jpg', BytesIO(b"fake_image"), 'image/jpeg')}
            response = client.post(
                "/api/v1/vision/analyze",
                headers=headers,
                files=files,
                data={'property_address': '123 Main St'}
            )
            
            assert response.status_code == 201
            scan_id = response.json()["id"]
            
            # Get scan details
            details_response = client.get(
                f"/api/v1/vision/preview/{scan_id}",
                headers=headers
            )
            assert details_response.status_code == 200
            
            # List scans
            list_response = client.get(
                "/api/v1/vision/scans",
                headers=headers
            )
            assert list_response.status_code == 200
            assert len(list_response.json()["scans"]) > 0


@pytest.mark.integration
@pytest.mark.db
def test_neighborhood_workflow(client, db, test_user):
    """Test complete neighborhood analysis workflow"""
    from app.models.user import User, SubscriptionTier
    from app.security.encryption import hash_password
    
    # Create authenticated user
    user = User(
        email="neighborhood_test@example.com",
        hashed_password=hash_password("password123"),
        full_name="Neighborhood Test User",
        subscription_tier=SubscriptionTier.PRO_AGENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "neighborhood_test@example.com",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Search neighborhood
    with patch('app.routers.neighborhood.WhisperAgent') as mock_whisper:
        mock_agent = Mock()
        mock_agent.analyze_neighborhood = AsyncMock(return_value={
            'location': 'Seattle, WA',
            'zip_code': '98101',
            'fit_score': 82.5,
            'amenities_score': 0.85,
            'sentiment_score': 0.75,
            'eco_score': 0.65,
            'forecast': {'trend': 'upward', 'demand_index': 8.5},
            'eco_roi': 5.2,
            'review_insights': [],
            'similar_neighborhoods': [],
            'market_data': {}
        })
        mock_whisper.return_value = mock_agent
        
        with patch('app.routers.neighborhood.check_tier_limit'):
            search_response = client.post(
                "/api/v1/neighborhood/search",
                headers=headers,
                json={
                    "query": "family-friendly neighborhood in Seattle",
                    "preferences": {"schools": "important"}
                }
            )
            
            assert search_response.status_code == 201
            report_id = search_response.json()["id"]
            
            # Get report details
            details_response = client.get(
                f"/api/v1/neighborhood/report/{report_id}",
                headers=headers
            )
            assert details_response.status_code == 200
            assert details_response.json()["fit_score"] == 82.5
            
            # List reports
            list_response = client.get(
                "/api/v1/neighborhood/reports",
                headers=headers
            )
            assert list_response.status_code == 200
            assert len(list_response.json()["reports"]) > 0


@pytest.mark.integration
@pytest.mark.db
def test_auth_workflow(client, db):
    """Test complete authentication workflow"""
    # Register
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "workflow_test@example.com",
            "password": "password123",
            "full_name": "Workflow Test User"
        }
    )
    assert register_response.status_code == 201
    refresh_token = register_response.json()["refresh_token"]
    
    # Get current user
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    
    # Update profile
    update_response = client.patch(
        "/api/v1/auth/me",
        headers=headers,
        json={"full_name": "Updated Name"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Updated Name"
    
    # Refresh token
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


@pytest.mark.integration
@pytest.mark.db
def test_calendar_with_neighborhood_integration(client, db, test_user):
    """Test calendar suggestions integrated with neighborhood reports"""
    from app.models.user import User, SubscriptionTier
    from app.models.neighborhood_report import NeighborhoodReport
    from app.security.encryption import hash_password
    
    # Create user
    user = User(
        email="calendar_test@example.com",
        hashed_password=hash_password("password123"),
        full_name="Calendar Test User",
        subscription_tier=SubscriptionTier.PRO_AGENT,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Create neighborhood report
    report = NeighborhoodReport(
        user_id=user.id,
        query="Seattle neighborhood",
        location="Seattle, WA",
        fit_score=85.0,
        status="completed",
        forecast={
            "demand_index": 9.0,
            "trend": "upward",
            "growth_rate_12_months": 0.08
        }
    )
    db.add(report)
    db.commit()
    
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "calendar_test@example.com",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get calendar suggestions
    suggest_response = client.post(
        "/api/v1/calendar/suggest",
        headers=headers,
        json={
            "location": "Seattle, WA",
            "max_suggestions": 5
        }
    )
    
    assert suggest_response.status_code == 200
    data = suggest_response.json()
    assert data["forecast_used"] is True
    assert len(data["suggestions"]) > 0
    assert data["suggestions"][0]["neighborhood_fit_score"] == 85.0

