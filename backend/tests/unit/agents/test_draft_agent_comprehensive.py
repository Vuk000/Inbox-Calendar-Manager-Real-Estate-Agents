"""
Comprehensive tests for Draft Agent
"""
import pytest
from unittest.mock import Mock
from app.agents.draft_agent import DraftAgent
from tests.mocks.claude_mock import MockClaudeAPI, MockClaudeMessage
from tests.fixtures.email_fixtures import *
from tests.fixtures.user_fixtures import *


@pytest.fixture
def draft_agent():
    """Create draft agent instance"""
    return DraftAgent()


@pytest.fixture
def agent_info():
    """Sample agent information"""
    return {
        "full_name": "Jane Smith",
        "email": "jane.smith@realestate.com",
        "phone_number": "(555) 123-4567",
        "brokerage": "Premium Realty"
    }


@pytest.fixture
def style_examples():
    """Sample writing style examples"""
    return [
        "Hi there! Thanks for reaching out. I'd love to help you find your dream home. Give me a call at your convenience!",
        "Hello! Great question. The property has 3 bedrooms and a beautiful backyard. Let me know if you'd like to schedule a showing.",
        "Thanks for your interest! I have several listings that might work for you. Can we set up a time to chat this week?"
    ]


class TestDraftAgentBasics:
    """Basic draft agent functionality"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, draft_agent):
        """Test agent initializes correctly"""
        assert draft_agent is not None
        assert draft_agent.client is not None
        assert draft_agent.model is not None
    
    def test_build_draft_prompt(self, draft_agent, lead_email, agent_info):
        """Test draft prompt building"""
        prompt = draft_agent._build_draft_prompt(
            lead_email, agent_info
        )
        
        assert isinstance(prompt, str)
        assert agent_info["full_name"] in prompt
        assert lead_email["subject"] in prompt
        assert "draft" in prompt.lower() or "response" in prompt.lower()
    
    def test_build_draft_prompt_with_style(self, draft_agent, lead_email, agent_info, style_examples):
        """Test prompt building with style examples"""
        prompt = draft_agent._build_draft_prompt(
            lead_email, agent_info, style_examples=style_examples
        )
        
        assert "style" in prompt.lower()
        assert any(ex[:50] in prompt for ex in style_examples)


class TestDraftGeneration:
    """Test draft generation"""
    
    @pytest.mark.asyncio
    async def test_generate_single_draft(self, draft_agent, lead_email, agent_info, monkeypatch):
        """Test generating single draft"""
        mock_response = MockClaudeAPI.get_draft_response()
        mock_message = MockClaudeMessage(mock_response["body"])
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(lead_email, agent_info)
        
        assert len(drafts) == 1
        assert "content" in drafts[0]
        assert "confidence_score" in drafts[0]
        assert drafts[0]["variant_number"] == 1
    
    @pytest.mark.asyncio
    async def test_generate_multiple_variants(self, draft_agent, lead_email, agent_info, monkeypatch):
        """Test generating multiple draft variants"""
        mock_response = MockClaudeAPI.get_draft_response()
        mock_message = MockClaudeMessage(mock_response["body"])
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(lead_email, agent_info, num_variants=3)
        
        assert len(drafts) == 3
        assert all("content" in d for d in drafts)
        assert all(d["variant_number"] in [1, 2, 3] for d in drafts)
    
    @pytest.mark.asyncio
    async def test_draft_with_style_examples(self, draft_agent, lead_email, agent_info, style_examples, monkeypatch):
        """Test draft generation with style matching"""
        mock_response = MockClaudeAPI.get_draft_response()
        mock_message = MockClaudeMessage(mock_response["body"])
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(
            lead_email, agent_info, style_examples=style_examples
        )
        
        assert len(drafts) == 1
        assert drafts[0]["confidence_score"] >= 0.8  # Higher confidence with style examples
    
    @pytest.mark.asyncio
    async def test_draft_with_context(self, draft_agent, lead_email, agent_info, monkeypatch):
        """Test draft generation with additional context"""
        context = {
            "crm_data": {"client_name": "Mike", "previous_interactions": 2},
            "property_data": {"address": "123 Main St", "price": "$350,000"}
        }
        
        mock_response = MockClaudeAPI.get_draft_response()
        mock_message = MockClaudeMessage(mock_response["body"])
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(
            lead_email, agent_info, context=context
        )
        
        assert len(drafts) == 1
        assert drafts[0]["content"]


class TestDraftForDifferentEmailTypes:
    """Test drafts for different email types"""
    
    @pytest.mark.asyncio
    async def test_draft_for_offer(self, draft_agent, offer_email, agent_info, monkeypatch):
        """Test draft for offer email"""
        mock_response = MockClaudeAPI.get_draft_response()
        mock_message = MockClaudeMessage(mock_response["body"])
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(offer_email, agent_info)
        
        assert len(drafts) == 1
        content = drafts[0]["content"].lower()
        # Should acknowledge offer professionally
        assert any(word in content for word in ["offer", "thank", "received"])
    
    @pytest.mark.asyncio
    async def test_draft_for_showing_request(self, draft_agent, showing_request_email, agent_info, monkeypatch):
        """Test draft for showing request"""
        mock_response = MockClaudeAPI.get_draft_response()
        mock_response["body"] = "Thank you for your interest in viewing the property. I have availability this Saturday at 2 PM. Would that work for you?"
        mock_message = MockClaudeMessage(mock_response["body"])
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(showing_request_email, agent_info)
        
        assert len(drafts) == 1
        content = drafts[0]["content"].lower()
        # Should address scheduling
        assert any(word in content for word in ["showing", "viewing", "schedule", "time", "available"])
    
    @pytest.mark.asyncio
    async def test_draft_for_counteroffer(self, draft_agent, counteroffer_email, agent_info, monkeypatch):
        """Test draft for counteroffer"""
        mock_response = MockClaudeAPI.get_draft_response()
        mock_message = MockClaudeMessage(mock_response["body"])
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(counteroffer_email, agent_info)
        
        assert len(drafts) == 1
        assert drafts[0]["content"]


class TestDraftMetadata:
    """Test draft metadata and analysis"""
    
    @pytest.mark.asyncio
    async def test_draft_includes_metadata(self, draft_agent, lead_email, agent_info, monkeypatch):
        """Test draft includes proper metadata"""
        mock_response = MockClaudeAPI.get_draft_response()
        mock_message = MockClaudeMessage(mock_response["body"])
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(lead_email, agent_info)
        
        draft = drafts[0]
        assert "generated_at" in draft
        assert "model_version" in draft
        assert "word_count" in draft
        assert "has_call_to_action" in draft
        assert draft["model_version"] == draft_agent.model
    
    @pytest.mark.asyncio
    async def test_call_to_action_detection(self, draft_agent, lead_email, agent_info, monkeypatch):
        """Test CTA detection in drafts"""
        mock_response = MockClaudeAPI.get_draft_response()
        mock_response["body"] = "Thanks for reaching out! Please call me at (555) 123-4567 to discuss further."
        mock_message = MockClaudeMessage(mock_response["body"])
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(lead_email, agent_info)
        
        assert drafts[0]["has_call_to_action"] is True
    
    @pytest.mark.asyncio
    async def test_word_count_calculation(self, draft_agent, lead_email, agent_info, monkeypatch):
        """Test word count is calculated"""
        mock_response = MockClaudeAPI.get_draft_response()
        mock_message = MockClaudeMessage("This is a short test draft with exactly ten words here.")
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(lead_email, agent_info)
        
        assert drafts[0]["word_count"] == 10


class TestDraftImprovement:
    """Test draft improvement based on feedback"""
    
    @pytest.mark.asyncio
    async def test_improve_draft(self, draft_agent, agent_info, monkeypatch):
        """Test improving draft with feedback"""
        original_draft = "Thank you for your email. I will get back to you soon."
        feedback = "Make it warmer and more enthusiastic"
        
        improved = "Thank you so much for reaching out! I'm excited to help you find your dream home. I'll get back to you within 24 hours!"
        mock_message = MockClaudeMessage(improved)
        
        mock_client = Mock()
        mock_client.messages.create = Mock(return_value=mock_message)
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        result = await draft_agent.improve_draft(original_draft, feedback, agent_info)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_improve_draft_error_handling(self, draft_agent, agent_info, monkeypatch):
        """Test error handling in draft improvement"""
        def mock_create_error(*args, **kwargs):
            raise Exception("API Error")
        
        mock_client = Mock()
        mock_client.messages.create = mock_create_error
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        result = await draft_agent.improve_draft("test", "make better", agent_info)
        
        assert "error" in result.lower()


class TestErrorHandling:
    """Test error handling"""
    
    @pytest.mark.asyncio
    async def test_generation_error_handling(self, draft_agent, lead_email, agent_info, monkeypatch):
        """Test graceful error handling"""
        def mock_create_error(*args, **kwargs):
            raise Exception("API Error")
        
        mock_client = Mock()
        mock_client.messages.create = mock_create_error
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(lead_email, agent_info)
        
        assert len(drafts) == 1
        assert "error" in drafts[0]
        assert drafts[0]["confidence_score"] == 0.0
    
    @pytest.mark.asyncio
    async def test_multiple_variants_partial_failure(self, draft_agent, lead_email, agent_info, monkeypatch):
        """Test handling when some variants fail"""
        call_count = [0]
        
        def mock_create_mixed(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("API Error on second call")
            mock_response = MockClaudeAPI.get_draft_response()
            return MockClaudeMessage(mock_response["body"])
        
        mock_client = Mock()
        mock_client.messages.create = mock_create_mixed
        monkeypatch.setattr(draft_agent, "client", mock_client)
        
        drafts = await draft_agent.generate_draft(lead_email, agent_info, num_variants=3)
        
        assert len(drafts) == 3
        # First and third should succeed, second should have error
        assert "error" not in drafts[0]
        assert "error" in drafts[1]
        assert "error" not in drafts[2]

