"""
Comprehensive tests for Triage Agent
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from app.agents.triage_agent import TriageAgent
from tests.mocks.claude_mock import MockClaudeAPI, MockClaudeMessage
from tests.fixtures.email_fixtures import *


@pytest.fixture
def triage_agent():
    """Create triage agent instance"""
    return TriageAgent()


@pytest.fixture
def mock_claude_client(monkeypatch):
    """Mock Anthropic Claude client"""
    mock_client = Mock()
    mock_messages = Mock()
    mock_client.messages = mock_messages
    return mock_client


class TestTriageAgentBasics:
    """Basic triage agent functionality"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, triage_agent):
        """Test agent initializes correctly"""
        assert triage_agent is not None
        assert triage_agent.client is not None
        assert triage_agent.model is not None
    
    @pytest.mark.asyncio
    async def test_build_prompt(self, triage_agent, offer_email):
        """Test prompt building"""
        prompt = triage_agent._build_prompt(offer_email)
        
        assert isinstance(prompt, str)
        assert offer_email["subject"] in prompt
        assert offer_email["sender_email"] in prompt
        assert "priority" in prompt.lower()
        assert "category" in prompt.lower()
        assert "entities" in prompt.lower()


class TestTriageHighPriority:
    """Test high priority email classification"""
    
    @pytest.mark.asyncio
    async def test_offer_email_high_priority(self, triage_agent, offer_email, monkeypatch):
        """Test offer email classified as high priority"""
        mock_response = MockClaudeAPI.get_triage_response(priority="high")
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(offer_email)
        
        assert result["priority"] == "high"
        assert result["urgency_score"] >= 70
        assert "category" in result
        assert "entities" in result
    
    @pytest.mark.asyncio
    async def test_inspection_report_urgent(self, triage_agent, inspection_report_email, monkeypatch):
        """Test inspection report marked as urgent"""
        mock_response = MockClaudeAPI.get_triage_response(priority="high")
        mock_response["category"] = "inspection"
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(inspection_report_email)
        
        assert result["priority"] in ["high", "medium"]
        assert result["requires_urgent_response"] or result["urgency_score"] > 60
    
    @pytest.mark.asyncio
    async def test_counteroffer_negotiation(self, triage_agent, counteroffer_email, monkeypatch):
        """Test counteroffer classified appropriately"""
        mock_response = MockClaudeAPI.get_triage_response(priority="high")
        mock_response["category"] = "counteroffer"
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(counteroffer_email)
        
        assert result["priority"] == "high"
        assert "suggested_actions" in result
        assert len(result["suggested_actions"]) > 0


class TestTriageMediumPriority:
    """Test medium priority email classification"""
    
    @pytest.mark.asyncio
    async def test_lead_inquiry_medium(self, triage_agent, lead_email, monkeypatch):
        """Test lead inquiry classified as medium"""
        mock_response = MockClaudeAPI.get_triage_response(priority="medium")
        mock_response["category"] = "lead"
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(lead_email)
        
        assert result["priority"] in ["medium", "high"]
        assert "reply" in result.get("suggested_actions", []) or len(result["suggested_actions"]) > 0
    
    @pytest.mark.asyncio
    async def test_showing_request_medium(self, triage_agent, showing_request_email, monkeypatch):
        """Test showing request classified appropriately"""
        mock_response = MockClaudeAPI.get_triage_response(priority="medium")
        mock_response["category"] = "showing_request"
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(showing_request_email)
        
        assert result["priority"] in ["medium", "high"]
        assert "schedule" in result.get("suggested_actions", []) or "reply" in result.get("suggested_actions", [])


class TestTriageLowPriority:
    """Test low priority email classification"""
    
    @pytest.mark.asyncio
    async def test_newsletter_low_priority(self, triage_agent, newsletter_email, monkeypatch):
        """Test newsletter classified as low priority"""
        mock_response = MockClaudeAPI.get_triage_response(priority="low")
        mock_response["category"] = "newsletter"
        mock_response["urgency_score"] = 20.0
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(newsletter_email)
        
        assert result["priority"] in ["low", "medium"]
        assert result["urgency_score"] < 60
    
    @pytest.mark.asyncio
    async def test_spam_detection(self, triage_agent, spam_email, monkeypatch):
        """Test spam detection"""
        mock_response = MockClaudeAPI.get_triage_response(priority="low")
        mock_response["category"] = "spam"
        mock_response["urgency_score"] = 5.0
        mock_response["suggested_actions"] = ["archive"]
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(spam_email)
        
        assert result["priority"] == "low"
        assert result["category"] in ["spam", "newsletter", "general"]


class TestEntityExtraction:
    """Test entity extraction capabilities"""
    
    @pytest.mark.asyncio
    async def test_extract_dollar_amounts(self, triage_agent, offer_email, monkeypatch):
        """Test dollar amount extraction"""
        mock_response = MockClaudeAPI.get_triage_response()
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(offer_email)
        
        entities = result.get("entities", {})
        dollar_amounts = entities.get("dollar_amounts", [])
        
        assert len(dollar_amounts) > 0
    
    @pytest.mark.asyncio
    async def test_extract_addresses(self, triage_agent, offer_email, monkeypatch):
        """Test address extraction"""
        mock_response = MockClaudeAPI.get_triage_response()
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(offer_email)
        
        entities = result.get("entities", {})
        addresses = entities.get("property_addresses", [])
        
        assert isinstance(addresses, list)
    
    def test_extract_addresses_utility(self, triage_agent):
        """Test address extraction utility method"""
        text = "Property at 123 Main Street and 456 Oak Avenue"
        addresses = triage_agent._extract_addresses(text)
        
        assert isinstance(addresses, list)
        assert len(addresses) >= 1
    
    def test_extract_dollars_utility(self, triage_agent):
        """Test dollar extraction utility method"""
        text = "Offer of $450,000 with $25,000 earnest money"
        amounts = triage_agent._extract_dollars(text)
        
        assert isinstance(amounts, list)
        assert len(amounts) >= 2


class TestFallbackBehavior:
    """Test fallback behavior when AI fails"""
    
    @pytest.mark.asyncio
    async def test_fallback_on_api_error(self, triage_agent, offer_email, monkeypatch):
        """Test fallback when API fails"""
        def mock_create_error(*args, **kwargs):
            raise Exception("API Error")
        
        mock_client = Mock()
        mock_client.messages.create = mock_create_error
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(offer_email)
        
        # Should still return valid structure
        assert "priority" in result
        assert "category" in result
        assert "error" in result
        assert result["model_version"] == "fallback"
        assert result["priority"] in ["high", "medium", "low"]
    
    @pytest.mark.asyncio
    async def test_fallback_on_json_decode_error(self, triage_agent, offer_email, monkeypatch):
        """Test fallback when JSON parsing fails"""
        mock_message = Mock()
        mock_message.content = [Mock(text="Invalid JSON {{{")]
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(offer_email)
        
        assert "priority" in result
        assert result["model_version"] == "fallback"
    
    def test_fallback_analysis(self, triage_agent, offer_email):
        """Test fallback analysis directly"""
        result = triage_agent._fallback_analysis(offer_email, "Test error")
        
        assert result["priority"] in ["high", "medium", "low"]
        assert result["category"] in ["offer", "lead", "general", "inspection", "showing_request"]
        assert "error" in result
        assert result["confidence"] < 0.5


class TestMultilingual:
    """Test multilingual support"""
    
    @pytest.mark.asyncio
    async def test_spanish_email(self, triage_agent, multilingual_email_spanish, monkeypatch):
        """Test Spanish language email"""
        mock_response = MockClaudeAPI.get_triage_response(priority="high")
        mock_response["category"] = "offer"
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(multilingual_email_spanish)
        
        assert "priority" in result
        assert result["entities"]["dollar_amounts"]


class TestResponseStructure:
    """Test response structure and validation"""
    
    @pytest.mark.asyncio
    async def test_response_has_required_fields(self, triage_agent, offer_email, monkeypatch):
        """Test response contains all required fields"""
        mock_response = MockClaudeAPI.get_triage_response()
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(offer_email)
        
        required_fields = [
            "priority", "urgency_score", "category", "entities",
            "suggested_actions", "sentiment_score", "key_points",
            "deadline_detected", "requires_urgent_response", "confidence"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
    
    @pytest.mark.asyncio
    async def test_response_includes_metadata(self, triage_agent, offer_email, monkeypatch):
        """Test response includes metadata"""
        mock_response = MockClaudeAPI.get_triage_response()
        mock_message = MockClaudeAPI.create_mock_message(mock_response)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(triage_agent, "client", mock_client)
        
        result = await triage_agent.analyze_email(offer_email)
        
        assert "model_version" in result
        assert "analyzed_at" in result
        assert result["model_version"] == triage_agent.model

