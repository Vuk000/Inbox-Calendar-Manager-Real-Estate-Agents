"""Tests for Neighborhood Whisper Router"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

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
def mock_whisper_agent():
    """Mock WhisperAgent"""
    with patch('app.routers.neighborhood.WhisperAgent') as mock:
        agent_instance = Mock()
        agent_instance.analyze_neighborhood = AsyncMock(return_value={
            'query': 'family-friendly Seattle',
            'location': 'Seattle, WA',
            'zip_code': '98101',
            'fit_score': 82.5,
            'amenities_score': 0.85,
            'sentiment_score': 0.75,
            'eco_score': 0.65,
            'forecast': {
                'trend': 'upward',
                'growth_rate_12_months': 0.07,
                'demand_index': 8.5
            },
            'eco_roi': 5.2,
            'review_insights': {
                'total_reviews': 50,
                'avg_rating': 4.5
            },
            'similar_neighborhoods': [
                {
                    'report_id': 1,
                    'score': 0.85,
                    'query': 'family-friendly Seattle',
                    'fit_score': 82.5
                }
            ]
        })
        mock.return_value = agent_instance
        yield agent_instance


@pytest.fixture
def mock_check_tier_limit():
    """Mock tier limit check"""
    with patch('app.routers.neighborhood.check_tier_limit') as mock:
        mock.return_value = None
        yield mock


def test_search_neighborhood_success(authenticated_client, mock_whisper_agent, mock_check_tier_limit):
    """Test successful neighborhood search"""
    request_data = {
        'query': 'family-friendly neighborhood in Seattle',
        'preferences': {'min_schools': 3}
    }
    
    response = authenticated_client.post(
        "/api/v1/neighborhood/search",
        json=request_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert 'id' in data
    assert 'query' in data
    assert 'fit_score' in data
    assert data['query'] == 'family-friendly neighborhood in Seattle'


def test_search_neighborhood_invalid_query(authenticated_client, mock_check_tier_limit):
    """Test neighborhood search with invalid query (too short)"""
    request_data = {
        'query': 'ab'  # Too short
    }
    
    response = authenticated_client.post(
        "/api/v1/neighborhood/search",
        json=request_data
    )
    
    assert response.status_code == 422  # Validation error


def test_search_neighborhood_unauthenticated(client):
    """Test that unauthenticated requests are rejected"""
    request_data = {
        'query': 'Seattle neighborhood'
    }
    
    response = client.post(
        "/api/v1/neighborhood/search",
        json=request_data
    )
    
    assert response.status_code == 401


def test_search_neighborhood_tier_limit_exceeded(authenticated_client, mock_check_tier_limit):
    """Test that tier limit exceptions are handled"""
    from app.shared.exceptions import SubscriptionLimitException
    
    mock_check_tier_limit.side_effect = SubscriptionLimitException(
        "Limit reached",
        feature="neighborhood_searches",
        limit=10,
        current_usage=10
    )
    
    request_data = {
        'query': 'Seattle neighborhood'
    }
    
    response = authenticated_client.post(
        "/api/v1/neighborhood/search",
        json=request_data
    )
    
    assert response.status_code == 403
    data = response.json()
    assert 'detail' in data
    assert 'limit' in data['detail']


def test_get_neighborhood_report_not_found(authenticated_client):
    """Test getting non-existent neighborhood report"""
    response = authenticated_client.get("/api/v1/neighborhood/reports/99999")
    
    assert response.status_code == 404


def test_list_neighborhood_reports(authenticated_client, test_user):
    """Test listing user's neighborhood reports"""
    from app.db import SessionLocal
    from app.models.neighborhood_report import NeighborhoodReport
    
    db = SessionLocal()
    try:
        report = NeighborhoodReport(
            user_id=test_user.id,
            query='family-friendly Seattle',
            location='Seattle, WA',
            fit_score=82.5,
            status='completed'
        )
        db.add(report)
        db.commit()
        report_id = report.id
        
        response = authenticated_client.get("/api/v1/neighborhood/reports")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should contain our test report
        report_ids = [r['id'] for r in data]
        assert report_id in report_ids
    finally:
        db.close()


def test_get_neighborhood_report_details(authenticated_client, test_user):
    """Test getting neighborhood report details"""
    from app.db import SessionLocal
    from app.models.neighborhood_report import NeighborhoodReport
    
    db = SessionLocal()
    try:
        report = NeighborhoodReport(
            user_id=test_user.id,
            query='family-friendly Seattle',
            location='Seattle, WA',
            zip_code='98101',
            fit_score=82.5,
            amenities_score=0.85,
            sentiment_score=0.75,
            eco_score=0.65,
            forecast={'trend': 'upward', 'growth_rate_12_months': 0.07},
            eco_roi=5.2,
            status='completed'
        )
        db.add(report)
        db.commit()
        report_id = report.id
        
        response = authenticated_client.get(f"/api/v1/neighborhood/reports/{report_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == report_id
        assert data['status'] == 'completed'
        assert data['fit_score'] == 82.5
        assert 'forecast' in data
        assert 'review_insights' in data
    finally:
        db.close()


def test_get_neighborhood_report_unauthorized(authenticated_client, test_user):
    """Test that users can't access other users' reports"""
    from app.db import SessionLocal
    from app.models.neighborhood_report import NeighborhoodReport
    from app.models.user import User
    
    db = SessionLocal()
    try:
        # Create another user
        other_user = User(
            email="other@example.com",
            password_hash="hash",
            full_name="Other User",
            subscription_tier=SubscriptionTier.FREE_TRIAL
        )
        db.add(other_user)
        db.commit()
        
        # Create report for other user
        report = NeighborhoodReport(
            user_id=other_user.id,
            query='Seattle neighborhood',
            location='Seattle, WA',
            fit_score=75.0,
            status='completed'
        )
        db.add(report)
        db.commit()
        report_id = report.id
        
        # Try to access with test_user
        response = authenticated_client.get(f"/api/v1/neighborhood/reports/{report_id}")
        
        assert response.status_code == 404  # Should not find (filtered by user)
    finally:
        db.close()


def test_search_neighborhood_agent_error(authenticated_client, mock_whisper_agent, mock_check_tier_limit):
    """Test handling of agent errors"""
    from app.shared.exceptions import NeighborhoodSearchException
    
    mock_whisper_agent.analyze_neighborhood = AsyncMock(
        side_effect=NeighborhoodSearchException("Analysis failed")
    )
    
    request_data = {
        'query': 'Seattle neighborhood'
    }
    
    response = authenticated_client.post(
        "/api/v1/neighborhood/search",
        json=request_data
    )
    
    assert response.status_code == 500
    data = response.json()
    assert 'detail' in data

