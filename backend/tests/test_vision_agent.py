"""Tests for VisionHome AI Agent"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import json

from app.agents.vision_agent import VisionAgent
from app.integrations.google_vision import GoogleVisionIntegration
from app.integrations.zillow_integration import ZillowIntegration, PropertyComp
from app.shared.exceptions import VisionProcessingException


@pytest.fixture
def mock_vision_integration():
    """Mock Google Vision integration"""
    mock = Mock(spec=GoogleVisionIntegration)
    mock.analyze_image_from_bytes = AsyncMock(return_value={
        'labels': [
            {'description': 'Kitchen', 'score': 0.95},
            {'description': 'Modern', 'score': 0.88},
            {'description': 'House', 'score': 0.92}
        ],
        'objects': [
            {'name': 'Refrigerator', 'score': 0.9, 'bounding_poly': []},
            {'name': 'Cabinet', 'score': 0.85, 'bounding_poly': []}
        ],
        'dominant_colors': [
            {'pixel_fraction': 0.4, 'color': {'red': 255, 'green': 255, 'blue': 255}}
        ]
    })
    return mock


@pytest.fixture
def mock_zillow_integration():
    """Mock Zillow integration"""
    mock = Mock(spec=ZillowIntegration)
    mock.get_comps = AsyncMock(return_value=[
        PropertyComp(
            address="123 Main St, Seattle, WA",
            price=450000.0,
            bedrooms=3,
            bathrooms=2.5,
            square_feet=1800,
            sold_date="2024-01-15"
        ),
        PropertyComp(
            address="456 Oak Ave, Seattle, WA",
            price=475000.0,
            bedrooms=4,
            bathrooms=3.0,
            square_feet=2100,
            sold_date="2024-02-20"
        )
    ])
    return mock


@pytest.fixture
def mock_claude_client():
    """Mock Claude/Anthropic client"""
    mock = Mock()
    mock.invoke = AsyncMock(return_value=Mock(
        content=json.dumps({
            'property_type': 'single_family_home',
            'property_style': 'modern',
            'condition_score': 0.85,
            'key_features': ['large kitchen', 'modern appliances', 'open floor plan'],
            'renovation_suggestions': ['kitchen remodel', 'bathroom upgrade'],
            'inferred_address_keywords': ['Seattle', 'residential'],
            'confidence_score': 0.88
        })
    ))
    return mock


@pytest.fixture
def vision_agent(mock_vision_integration, mock_zillow_integration, mock_claude_client):
    """Create VisionAgent with mocked dependencies"""
    with patch('app.agents.vision_agent.ChatAnthropic', return_value=mock_claude_client):
        agent = VisionAgent(
            vision_integration=mock_vision_integration,
            zillow_integration=mock_zillow_integration
        )
        agent.analysis_chain = Mock()
        agent.analysis_chain.invoke = AsyncMock(return_value={
            'property_type': 'single_family_home',
            'property_style': 'modern',
            'condition_score': 0.85,
            'key_features': ['large kitchen', 'modern appliances'],
            'renovation_suggestions': ['kitchen remodel', 'bathroom upgrade'],
            'inferred_address_keywords': ['Seattle'],
            'confidence_score': 0.88
        })
        return agent


@pytest.mark.asyncio
async def test_analyze_property_image_success(vision_agent, mock_vision_integration, mock_zillow_integration):
    """Test successful property image analysis"""
    image_bytes = b"fake_image_data"
    property_address = "123 Main St, Seattle, WA"
    
    result = await vision_agent.analyze_property_image(
        image_bytes=image_bytes,
        property_address=property_address
    )
    
    # Verify Vision API was called
    mock_vision_integration.analyze_image_from_bytes.assert_called_once_with(image_bytes)
    
    # Verify Zillow API was called
    mock_zillow_integration.get_comps.assert_called_once()
    
    # Verify result structure
    assert 'vision_analysis' in result
    assert 'llm_interpretation' in result
    assert 'similar_properties' in result
    assert 'timestamp' in result
    
    # Verify LLM interpretation
    assert result['llm_interpretation']['property_type'] == 'single_family_home'
    assert result['llm_interpretation']['condition_score'] == 0.85


@pytest.mark.asyncio
async def test_analyze_property_image_no_address(vision_agent, mock_vision_integration):
    """Test property image analysis without address"""
    image_bytes = b"fake_image_data"
    
    result = await vision_agent.analyze_property_image(
        image_bytes=image_bytes,
        property_address=None
    )
    
    # Should still work without address
    assert 'vision_analysis' in result
    assert 'llm_interpretation' in result
    # Should not have similar properties without address
    assert 'similar_properties' in result


@pytest.mark.asyncio
async def test_analyze_property_image_vision_error(vision_agent, mock_vision_integration):
    """Test handling of Vision API errors"""
    mock_vision_integration.analyze_image_from_bytes = AsyncMock(
        side_effect=VisionProcessingException("Vision API error")
    )
    
    image_bytes = b"fake_image_data"
    
    with pytest.raises(VisionProcessingException):
        await vision_agent.analyze_property_image(
            image_bytes=image_bytes,
            property_address=None
        )


@pytest.mark.asyncio
async def test_analyze_property_image_zillow_fallback(vision_agent, mock_vision_integration, mock_zillow_integration):
    """Test that Zillow errors don't break the flow"""
    mock_zillow_integration.get_comps = AsyncMock(side_effect=Exception("Zillow API error"))
    
    image_bytes = b"fake_image_data"
    property_address = "123 Main St"
    
    # Should still succeed even if Zillow fails
    result = await vision_agent.analyze_property_image(
        image_bytes=image_bytes,
        property_address=property_address
    )
    
    assert 'vision_analysis' in result
    assert 'llm_interpretation' in result
    # Should handle Zillow error gracefully
    assert isinstance(result.get('similar_properties'), list)


def test_create_feature_vector_from_llm_analysis(vision_agent):
    """Test feature vector creation from LLM analysis"""
    llm_analysis = {
        'property_type': 'single_family_home',
        'condition_score': 0.85
    }
    
    features = vision_agent._create_feature_vector_from_llm_analysis(llm_analysis)
    
    assert isinstance(features, list)
    assert len(features) > 0
    assert features[0] == 0.85  # condition_score


def test_create_feature_vector_from_property_comp(vision_agent):
    """Test feature vector creation from PropertyComp"""
    comp = PropertyComp(
        address="123 Main St",
        price=450000.0,
        bedrooms=3,
        bathrooms=2.5,
        square_feet=1800,
        sold_date="2024-01-15"
    )
    
    features = vision_agent._create_feature_vector_from_property_comp(comp)
    
    assert isinstance(features, list)
    assert len(features) == 4
    assert features[0] == 450000.0  # price
    assert features[1] == 3.0  # bedrooms

