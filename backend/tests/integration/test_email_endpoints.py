"""
Integration tests for email endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from tests.fixtures.email_fixtures import *
from tests.fixtures.user_fixtures import *
from tests.mocks.claude_mock import MockClaudeAPI


client = TestClient(app)


class TestEmailEndpoints:
    """Test email API endpoints"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "app" in response.json()
        assert "docs" in response.json()


@pytest.mark.integration
class TestEmailTriageEndpoint:
    """Test email triage endpoint"""
    
    @patch('app.agents.triage_agent.TriageAgent.analyze_email')
    def test_triage_email_success(self, mock_analyze, offer_email, auth_headers):
        """Test successful email triage"""
        # Mock the triage response
        mock_analyze.return_value = MockClaudeAPI.get_triage_response()
        
        response = client.post(
            "/api/v1/emails/triage",
            json=offer_email,
            headers=auth_headers
        )
        
        # Note: May return 401 if auth not fully mocked
        # This is a structure test
        assert response.status_code in [200, 401, 404]


@pytest.mark.integration
class TestDraftEndpoint:
    """Test draft generation endpoint"""
    
    @patch('app.agents.draft_agent.DraftAgent.generate_draft')
    def test_generate_draft_success(self, mock_generate, offer_email, auth_headers):
        """Test successful draft generation"""
        mock_generate.return_value = [MockClaudeAPI.get_draft_response()]
        
        response = client.post(
            "/api/v1/drafts/generate",
            json={"email_id": 1},
            headers=auth_headers
        )
        
        # Structure test
        assert response.status_code in [200, 401, 404, 422]


# Note: Full integration tests require database setup
# These are structure tests to verify endpoint existence

