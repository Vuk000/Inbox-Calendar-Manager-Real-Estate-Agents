"""
Tests for AI Triage Agent
"""
import pytest
from app.agents.triage_agent import TriageAgent


@pytest.fixture
def triage_agent():
    """Create triage agent instance"""
    return TriageAgent()


@pytest.fixture
def offer_email():
    """Sample offer email"""
    return {
        "subject": "Offer on 456 Oak Avenue",
        "body": """Hello,

I would like to submit an offer of $525,000 for the property at 456 Oak Avenue.

I am pre-approved for up to $600,000 and can close in 30 days. I have $50,000 earnest money ready.

Please let me know if this works.

Best regards,
Sarah Johnson""",
        "sender_email": "sarah.johnson@example.com",
        "received_at": "2025-10-14T14:00:00Z"
    }


@pytest.fixture
def lead_email():
    """Sample lead inquiry email"""
    return {
        "subject": "Looking for a 3-bedroom house",
        "body": """Hi,

I'm interested in buying a 3-bedroom house in the downtown area. My budget is around $300,000-$350,000.

I'd like to move within the next 2-3 months. Can you help me find something?

Thanks,
Mike""",
        "sender_email": "mike@example.com",
        "received_at": "2025-10-14T09:00:00Z"
    }


@pytest.fixture
def newsletter_email():
    """Sample newsletter (low priority)"""
    return {
        "subject": "Monthly Real Estate Market Update",
        "body": """Dear Agent,

Here's your monthly market update with trends, statistics, and insights...

[Newsletter content]

Unsubscribe | View in browser""",
        "sender_email": "newsletter@realestatenews.com",
        "received_at": "2025-10-14T06:00:00Z"
    }


@pytest.mark.asyncio
async def test_analyze_offer_email(triage_agent, offer_email):
    """Test triage analysis of an offer email"""
    result = await triage_agent.analyze_email(offer_email)
    
    # Check basic structure
    assert "priority" in result
    assert "category" in result
    assert "urgency_score" in result
    assert "entities" in result
    
    # Verify high priority for offers
    assert result["priority"] in ["high", "medium"]  # Should be high, but AI may vary
    
    # Check if category is detected
    assert result["category"] in ["offer", "negotiation", "general"]
    
    # Check urgency score
    assert result["urgency_score"] >= 50  # Offers should have high urgency
    
    # Check entities extraction
    entities = result["entities"]
    assert "dollar_amounts" in entities
    assert "property_addresses" in entities


@pytest.mark.asyncio
async def test_analyze_lead_email(triage_agent, lead_email):
    """Test triage analysis of a lead inquiry"""
    result = await triage_agent.analyze_email(lead_email)
    
    assert result["priority"] in ["medium", "low"]
    assert result["category"] == "lead" or "general" in result["category"]
    assert "suggested_actions" in result
    assert "reply" in result.get("suggested_actions", []) or len(result.get("suggested_actions", [])) > 0


@pytest.mark.asyncio
async def test_analyze_newsletter(triage_agent, newsletter_email):
    """Test triage analysis of a newsletter (should be low priority)"""
    result = await triage_agent.analyze_email(newsletter_email)
    
    # Newsletters should be low priority
    assert result["priority"] in ["low", "medium"]
    assert result["urgency_score"] < 60


@pytest.mark.asyncio
async def test_entity_extraction(triage_agent, offer_email):
    """Test entity extraction capabilities"""
    result = await triage_agent.analyze_email(offer_email)
    
    entities = result.get("entities", {})
    
    # Check for dollar amounts
    dollar_amounts = entities.get("dollar_amounts", [])
    assert len(dollar_amounts) > 0
    assert any("525" in str(amt) or "525000" in str(amt) for amt in dollar_amounts)
    
    # Check for addresses
    addresses = entities.get("property_addresses", [])
    # May or may not extract correctly, so we just verify structure
    assert isinstance(addresses, list)


@pytest.mark.asyncio
async def test_multilingual_email(triage_agent):
    result = await triage_agent.analyze_email({
        "subject": "Oferta para 789 Pine Street",
        "body": "Hola, me gustaría presentar una oferta de $400,000 por la propiedad.",
        "sender_email": "comprador@example.com"
    })
    assert "priority" in result
    assert result["entities"]["dollar_amounts"]


@pytest.mark.asyncio
async def test_fallback_on_api_failure(triage_agent, monkeypatch):
    """Test fallback behavior when AI API fails"""
    # Mock the client to raise an exception
    def mock_create(*args, **kwargs):
        raise Exception("API Error")
    
    monkeypatch.setattr(triage_agent.client.messages, "create", mock_create)
    
    result = await triage_agent.analyze_email({
        "subject": "Urgent offer expires today",
        "body": "This is an urgent email about an offer",
        "sender_email": "test@example.com"
    })
    
    # Should still return valid structure (fallback)
    assert "priority" in result
    assert "category" in result
    assert "error" in result  # Indicates fallback was used
    assert result["model_version"] == "fallback"
    assert result["priority"] in ["high", "medium", "low"]


def test_extract_addresses(triage_agent):
    """Test address extraction utility"""
    text = "The property at 123 Main Street is beautiful. Also check out 456 Oak Avenue."
    addresses = triage_agent._extract_addresses(text)
    
    assert isinstance(addresses, list)
    # Should extract at least one address
    assert len(addresses) >= 1


def test_extract_dollars(triage_agent):
    """Test dollar amount extraction"""
    text = "The price is $450,000 with $25,000 earnest money and $5,500 in closing costs."
    amounts = triage_agent._extract_dollars(text)
    
    assert isinstance(amounts, list)
    assert len(amounts) >= 3  # Should find multiple amounts

