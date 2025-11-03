"""Tests for Calendar Router"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Test client"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def authenticated_client(client, test_user, test_token):
    """Client with authentication"""
    client.headers.update({"Authorization": f"Bearer {test_token}"})
    return client


@pytest.mark.unit
@pytest.mark.db
def test_suggest_calendar_events_success(authenticated_client, test_user):
    """Test successful calendar event suggestions"""
    from app.db import SessionLocal
    from app.models.neighborhood_report import NeighborhoodReport
    
    db = SessionLocal()
    try:
        # Create a neighborhood report with forecast
        report = NeighborhoodReport(
            user_id=test_user.id,
            query="family-friendly Seattle",
            location="Seattle, WA",
            fit_score=82.5,
            status="completed",
            forecast={
                "trend": "upward",
                "demand_index": 8.5,
                "growth_rate_12_months": 0.07
            }
        )
        db.add(report)
        db.commit()
        
        request_data = {
            "location": "Seattle, WA",
            "date_range_start": datetime.utcnow().isoformat(),
            "date_range_end": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "event_type": "property_showing",
            "max_suggestions": 5
        }
        
        response = authenticated_client.post(
            "/api/v1/calendar/suggest",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0
        assert data["forecast_used"] is True
        assert "location" in data
        
        # Verify suggestion structure
        suggestion = data["suggestions"][0]
        assert "suggested_date" in suggestion
        assert "suggested_time" in suggestion
        assert "confidence_score" in suggestion
        assert "reasoning" in suggestion
    finally:
        db.close()


@pytest.mark.unit
@pytest.mark.db
def test_suggest_calendar_events_no_forecast(authenticated_client):
    """Test calendar suggestions without neighborhood forecast"""
    request_data = {
        "location": "Unknown Location",
        "date_range_start": datetime.utcnow().isoformat(),
        "date_range_end": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "max_suggestions": 3
    }
    
    response = authenticated_client.post(
        "/api/v1/calendar/suggest",
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0
    assert data["forecast_used"] is False


@pytest.mark.unit
@pytest.mark.db
def test_suggest_calendar_events_default_date_range(authenticated_client):
    """Test calendar suggestions with default date range"""
    request_data = {
        "location": "Seattle, WA",
        "max_suggestions": 5
    }
    
    response = authenticated_client.post(
        "/api/v1/calendar/suggest",
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0


@pytest.mark.unit
def test_suggest_calendar_events_unauthenticated(client):
    """Test that unauthenticated requests are rejected"""
    request_data = {
        "location": "Seattle, WA",
        "max_suggestions": 5
    }
    
    response = client.post(
        "/api/v1/calendar/suggest",
        json=request_data
    )
    
    assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.db
def test_suggest_calendar_events_invalid_max(authenticated_client):
    """Test calendar suggestions with invalid max_suggestions"""
    request_data = {
        "location": "Seattle, WA",
        "max_suggestions": 25  # Exceeds limit of 20
    }
    
    response = authenticated_client.post(
        "/api/v1/calendar/suggest",
        json=request_data
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
@pytest.mark.db
def test_suggest_calendar_events_open_house_type(authenticated_client, test_user):
    """Test calendar suggestions for open house event type"""
    from app.db import SessionLocal
    from app.models.neighborhood_report import NeighborhoodReport
    
    db = SessionLocal()
    try:
        report = NeighborhoodReport(
            user_id=test_user.id,
            query="Seattle",
            location="Seattle, WA",
            fit_score=75.0,
            status="completed",
            forecast={"demand_index": 7.0}
        )
        db.add(report)
        db.commit()
        
        request_data = {
            "location": "Seattle, WA",
            "event_type": "open_house",
            "max_suggestions": 3
        }
        
        response = authenticated_client.post(
            "/api/v1/calendar/suggest",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) > 0
        # Open house should have longer duration
        assert data["suggestions"][0]["recommended_duration_minutes"] == 120
    finally:
        db.close()


@pytest.mark.unit
@pytest.mark.db
def test_get_calendar_suggestions_legacy(authenticated_client):
    """Test legacy GET endpoint for calendar suggestions"""
    response = authenticated_client.get(
        "/api/v1/calendar/suggestions",
        params={
            "location": "Seattle, WA",
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data

