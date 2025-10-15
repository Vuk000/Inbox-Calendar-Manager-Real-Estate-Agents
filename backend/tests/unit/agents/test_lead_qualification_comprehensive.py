"""
Comprehensive tests for Lead Qualification Agent
"""
import pytest
import json
from unittest.mock import Mock
from app.agents.lead_qualification_agent import LeadQualificationAgent
from tests.mocks.claude_mock import MockClaudeAPI, MockClaudeMessage
from tests.fixtures.email_fixtures import *


@pytest.fixture
def lead_qual_agent():
    """Create lead qualification agent instance"""
    return LeadQualificationAgent()


class TestLeadQualificationBasics:
    """Basic lead qualification functionality"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, lead_qual_agent):
        """Test agent initializes correctly"""
        assert lead_qual_agent is not None
        assert lead_qual_agent.client is not None
        assert lead_qual_agent.model is not None


class TestLeadScoring:
    """Test lead scoring functionality"""
    
    @pytest.mark.asyncio
    async def test_qualify_hot_lead(self, lead_qual_agent, lead_email, monkeypatch):
        """Test hot lead scoring (80-100)"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["lead_score"] = 90
        mock_response["qualification_factors"]["urgency_level"] = "high"
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        assert result["lead_score"] >= 80
        assert result["qualification_factors"]["urgency_level"] == "high"
    
    @pytest.mark.asyncio
    async def test_qualify_warm_lead(self, lead_qual_agent, lead_email, monkeypatch):
        """Test warm lead scoring (50-79)"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["lead_score"] = 65
        mock_response["qualification_factors"]["urgency_level"] = "medium"
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        assert 50 <= result["lead_score"] < 80
    
    @pytest.mark.asyncio
    async def test_qualify_cold_lead(self, lead_qual_agent, newsletter_email, monkeypatch):
        """Test cold lead scoring (0-49)"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["lead_score"] = 30
        mock_response["qualification_factors"]["urgency_level"] = "low"
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(newsletter_email)
        
        assert result["lead_score"] < 50


class TestQualificationFactors:
    """Test qualification factor extraction"""
    
    @pytest.mark.asyncio
    async def test_extract_budget_info(self, lead_qual_agent, lead_email, monkeypatch):
        """Test budget extraction"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["qualification_factors"]["budget_mentioned"] = True
        mock_response["qualification_factors"]["budget_range"] = "$300,000-$350,000"
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        factors = result["qualification_factors"]
        assert factors["budget_mentioned"] is True
        assert factors["budget_range"] == "$300,000-$350,000"
    
    @pytest.mark.asyncio
    async def test_extract_timeline(self, lead_qual_agent, lead_email, monkeypatch):
        """Test timeline extraction"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["qualification_factors"]["timeline_mentioned"] = True
        mock_response["qualification_factors"]["timeline"] = "next 2-3 months"
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        factors = result["qualification_factors"]
        assert factors["timeline_mentioned"] is True
        assert "month" in factors["timeline"].lower()
    
    @pytest.mark.asyncio
    async def test_extract_property_preferences(self, lead_qual_agent, lead_email, monkeypatch):
        """Test property preference extraction"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["qualification_factors"]["property_type"] = "house"
        mock_response["qualification_factors"]["bedrooms"] = 3
        mock_response["qualification_factors"]["locations"] = ["downtown"]
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        factors = result["qualification_factors"]
        assert factors["property_type"] == "house"
        assert factors["bedrooms"] == 3
        assert "downtown" in factors["locations"]
    
    @pytest.mark.asyncio
    async def test_buyer_or_seller_detection(self, lead_qual_agent, lead_email, monkeypatch):
        """Test buyer/seller classification"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["qualification_factors"]["buyer_or_seller"] = "buyer"
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        assert result["qualification_factors"]["buyer_or_seller"] == "buyer"


class TestIntentAnalysis:
    """Test intent analysis"""
    
    @pytest.mark.asyncio
    async def test_primary_intent_buy(self, lead_qual_agent, lead_email, monkeypatch):
        """Test buy intent detection"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["intent_analysis"] = {
            "primary_intent": "buy",
            "motivation": "upgrade",
            "pain_points": ["limited inventory"],
            "objections": []
        }
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        intent = result.get("intent_analysis", {})
        assert intent["primary_intent"] == "buy"
    
    @pytest.mark.asyncio
    async def test_spam_detection(self, lead_qual_agent, spam_email, monkeypatch):
        """Test spam intent detection"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["lead_score"] = 0
        mock_response["intent_analysis"] = {
            "primary_intent": "spam",
            "motivation": "unknown",
            "pain_points": [],
            "objections": []
        }
        mock_response["recommended_actions"] = ["ignore"]
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(spam_email)
        
        intent = result.get("intent_analysis", {})
        assert intent["primary_intent"] == "spam"
        assert "ignore" in result["recommended_actions"]


class TestRecommendedActions:
    """Test recommended action generation"""
    
    @pytest.mark.asyncio
    async def test_hot_lead_actions(self, lead_qual_agent, offer_email, monkeypatch):
        """Test recommended actions for hot leads"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["lead_score"] = 95
        mock_response["recommended_actions"] = ["call_immediately", "send_listings"]
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(offer_email)
        
        actions = result["recommended_actions"]
        assert "call_immediately" in actions or "send_listings" in actions
    
    @pytest.mark.asyncio
    async def test_auto_response_suggestion(self, lead_qual_agent, lead_email, monkeypatch):
        """Test auto-response suggestion"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["auto_response_suggested"] = True
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        assert "auto_response_suggested" in result


class TestCRMIntegration:
    """Test CRM tagging and integration features"""
    
    @pytest.mark.asyncio
    async def test_crm_tags_generated(self, lead_qual_agent, lead_email, monkeypatch):
        """Test CRM tags are suggested"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_response["crm_tags"] = ["first-time-buyer", "downtown", "3BR", "hot-lead"]
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        assert "crm_tags" in result
        assert isinstance(result["crm_tags"], list)
        assert len(result["crm_tags"]) > 0


class TestQualifyingQuestions:
    """Test qualifying question generation"""
    
    @pytest.mark.asyncio
    async def test_generate_questions_for_incomplete_lead(self, lead_qual_agent, monkeypatch):
        """Test question generation for incomplete leads"""
        lead_data = {
            "qualification_factors": {
                "budget_mentioned": False,
                "timeline_mentioned": False,
                "location_specified": True
            }
        }
        
        questions = "Thanks for reaching out! I'd love to help you. Could you share your budget range and timeline?"
        mock_message = MockClaudeMessage(questions)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.generate_qualification_questions(lead_data)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_questions_error_fallback(self, lead_qual_agent, monkeypatch):
        """Test fallback for question generation errors"""
        lead_data = {"qualification_factors": {}}
        
        def mock_create_error(*args, **kwargs):
            raise Exception("API Error")
        
        mock_client = Mock()
        mock_client.messages.create = mock_create_error
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.generate_qualification_questions(lead_data)
        
        # Should return fallback message
        assert isinstance(result, str)
        assert len(result) > 0


class TestMetadata:
    """Test metadata and response structure"""
    
    @pytest.mark.asyncio
    async def test_includes_metadata(self, lead_qual_agent, lead_email, monkeypatch):
        """Test response includes metadata"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        assert "qualified_at" in result
        assert "model_version" in result
        assert result["model_version"] == lead_qual_agent.model
    
    @pytest.mark.asyncio
    async def test_confidence_score(self, lead_qual_agent, lead_email, monkeypatch):
        """Test confidence score is included"""
        mock_response = MockClaudeAPI.get_lead_qualification_response()
        mock_message = MockClaudeMessage(json.dumps(mock_response))
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1


class TestErrorHandling:
    """Test error handling and fallback"""
    
    @pytest.mark.asyncio
    async def test_api_error_fallback(self, lead_qual_agent, lead_email, monkeypatch):
        """Test fallback when API fails"""
        def mock_create_error(*args, **kwargs):
            raise Exception("API Error")
        
        mock_client = Mock()
        mock_client.messages.create = mock_create_error
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        # Should return fallback structure
        assert "lead_score" in result
        assert result["lead_score"] == 50  # Default medium score
        assert "error" in result
        assert result["confidence"] < 0.5
    
    @pytest.mark.asyncio
    async def test_json_parse_error_fallback(self, lead_qual_agent, lead_email, monkeypatch):
        """Test fallback when JSON parsing fails"""
        mock_message = MockClaudeMessage("Invalid JSON {{{")
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(lead_qual_agent, "client", mock_client)
        
        result = await lead_qual_agent.qualify_lead(lead_email)
        
        assert "lead_score" in result
        assert "error" in result

