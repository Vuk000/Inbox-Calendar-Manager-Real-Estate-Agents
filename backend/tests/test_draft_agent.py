"""
Tests for AI Draft Agent
"""
import pytest
from app.agents.draft_agent import DraftAgent


@pytest.fixture
def draft_agent():
    """Create draft agent instance"""
    return DraftAgent()


@pytest.fixture
def lead_inquiry():
    """Sample lead inquiry to reply to"""
    return {
        "subject": "Interested in downtown condos",
        "body": """Hi,

I saw your listing for condos downtown. I'm looking for a 2-bedroom unit, budget around $400K.

Can you send me more information?

Thanks,
Jessica""",
        "sender_email": "jessica@example.com",
        "sender_name": "Jessica Martinez"
    }


@pytest.fixture
def agent_info():
    """Sample agent information"""
    return {
        "full_name": "Jane Smith",
        "email": "jane.smith@realty.com",
        "phone_number": "+1-555-123-4567"
    }


@pytest.mark.asyncio
async def test_generate_single_draft(draft_agent, lead_inquiry, agent_info):
    """Test generating a single draft"""
    drafts = await draft_agent.generate_draft(
        original_email=lead_inquiry,
        agent_info=agent_info,
        num_variants=1
    )
    
    assert len(drafts) == 1
    draft = drafts[0]
    
    # Check structure
    assert "content" in draft
    assert "confidence_score" in draft
    assert "variant_number" in draft
    assert draft["variant_number"] == 1
    
    # Check content is not empty
    assert len(draft["content"]) > 50
    
    # Check for professional elements
    content_lower = draft["content"].lower()
    assert "jessica" in content_lower or "hi" in content_lower  # Personalization


@pytest.mark.asyncio
async def test_generate_multiple_variants(draft_agent, lead_inquiry, agent_info):
    """Test generating multiple draft variants"""
    drafts = await draft_agent.generate_draft(
        original_email=lead_inquiry,
        agent_info=agent_info,
        num_variants=3
    )
    
    assert len(drafts) == 3
    
    # Each should have different variant number
    variant_numbers = [d["variant_number"] for d in drafts]
    assert variant_numbers == [1, 2, 3]
    
    # All should have content
    for draft in drafts:
        assert len(draft["content"]) > 20


@pytest.mark.asyncio
async def test_draft_with_style_examples(draft_agent, lead_inquiry, agent_info):
    """Test draft generation with style examples"""
    style_examples = [
        "Hey there! Thanks for reaching out. I'd love to help you find your dream home. Let's schedule a call to discuss your needs. Call me at 555-1234!",
        "Hi! Great to hear from you. I have several properties that might interest you. When can we chat? Best, Jane"
    ]
    
    drafts = await draft_agent.generate_draft(
        original_email=lead_inquiry,
        agent_info=agent_info,
        style_examples=style_examples,
        num_variants=1
    )
    
    assert len(drafts) == 1
    # Should have higher confidence with style examples
    assert drafts[0]["confidence_score"] >= 0.7


@pytest.mark.asyncio
async def test_improve_draft_with_feedback(draft_agent, agent_info):
    """Test draft improvement based on feedback"""
    original_draft = "Thanks for your interest. I'll send you listings."
    feedback = "Make it warmer and more personal. Mention scheduling a call."
    
    improved = await draft_agent.improve_draft(
        original_draft=original_draft,
        feedback=feedback,
        agent_info=agent_info
    )
    
    # Check that improvement was attempted
    assert len(improved) > len(original_draft)
    assert "call" in improved.lower() or "phone" in improved.lower()


@pytest.mark.asyncio
async def test_draft_includes_contact_info(draft_agent, lead_inquiry, agent_info):
    """Test that drafts include agent contact information"""
    drafts = await draft_agent.generate_draft(
        original_email=lead_inquiry,
        agent_info=agent_info,
        num_variants=1
    )
    
    content = drafts[0]["content"]
    
    # Should mention agent's name or contact details
    assert (
        agent_info["full_name"] in content or
        agent_info["phone_number"] in content or
        "jane" in content.lower()
    )


@pytest.mark.asyncio
async def test_draft_has_call_to_action(draft_agent, lead_inquiry, agent_info):
    """Test that drafts include a call-to-action"""
    drafts = await draft_agent.generate_draft(
        original_email=lead_inquiry,
        agent_info=agent_info,
        num_variants=1
    )
    
    draft = drafts[0]
    
    # Should have call to action flag
    assert "has_call_to_action" in draft
    
    content_lower = draft["content"].lower()
    cta_keywords = ["call", "schedule", "meet", "let me know", "reach out", "contact"]
    
    has_cta = any(keyword in content_lower for keyword in cta_keywords)
    assert has_cta or draft["has_call_to_action"]

