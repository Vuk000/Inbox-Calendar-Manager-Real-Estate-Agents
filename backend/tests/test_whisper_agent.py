"""Tests for Neighborhood Whisper Agent"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import json

from app.agents.whisper_agent import WhisperAgent
from app.integrations.yelp import YelpIntegration
from app.integrations.vector_store import VectorStore
from app.shared.exceptions import NeighborhoodSearchException


@pytest.fixture
def mock_yelp_client():
    """Mock Yelp integration"""
    mock = Mock(spec=YelpIntegration)
    mock.get_neighborhood_reviews = Mock(return_value=[
        {
            'business_id': 'biz1',
            'name': 'Great Restaurant',
            'reviews': [
                {'text': 'Amazing place!', 'rating': 5},
                {'text': 'Love it here', 'rating': 5}
            ]
        },
        {
            'business_id': 'biz2',
            'name': 'Beautiful Park',
            'reviews': [
                {'text': 'Perfect for families', 'rating': 4}
            ]
        }
    ])
    mock.extract_sentiment_from_reviews = Mock(return_value={
        'sentiment_score': 0.75,
        'total_reviews': 3,
        'avg_rating': 4.67
    })
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock Pinecone vector store"""
    mock = Mock(spec=VectorStore)
    mock.search_similar_neighborhoods = AsyncMock(return_value={
        'success': True,
        'matches': [
            {
                'report_id': 1,
                'score': 0.85,
                'query': 'family-friendly Seattle',
                'fit_score': 82.5
            }
        ],
        'count': 1
    })
    return mock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    mock = Mock()
    mock.invoke = AsyncMock(return_value=Mock(
        content=json.dumps({
            'location': 'Seattle, WA',
            'zip_code': '98101',
            'amenities': ['parks', 'schools', 'restaurants'],
            'lifestyle': ['family-friendly', 'quiet']
        })
    ))
    return mock


@pytest.fixture
def whisper_agent(mock_yelp_client, mock_vector_store, mock_openai_client):
    """Create WhisperAgent with mocked dependencies"""
    with patch('app.agents.whisper_agent.ChatOpenAI', return_value=mock_openai_client), \
         patch('app.agents.whisper_agent.OpenAIEmbeddings') as mock_embeddings:
        
        mock_embeddings_instance = Mock()
        mock_embeddings_instance.aembed_query = AsyncMock(return_value=[0.1] * 1536)
        mock_embeddings.return_value = mock_embeddings_instance
        
        agent = WhisperAgent(
            yelp_integration=mock_yelp_client,
            vector_store=mock_vector_store
        )
        
        # Mock the NLP chain
        agent.nlp_chain = Mock()
        agent.nlp_chain.invoke = AsyncMock(return_value={
            'location': 'Seattle, WA',
            'zip_code': '98101',
            'amenities': ['parks', 'schools'],
            'lifestyle': ['family-friendly']
        })
        
        # Mock sentiment chain
        agent.sentiment_chain = Mock()
        agent.sentiment_chain.invoke = AsyncMock(return_value=Mock(content='0.75'))
        
        return agent


@pytest.mark.asyncio
async def test_analyze_neighborhood_success(whisper_agent, mock_yelp_client, mock_vector_store):
    """Test successful neighborhood analysis"""
    query = "family-friendly neighborhood in Seattle"
    
    result = await whisper_agent.analyze_neighborhood(
        query=query,
        user_preferences={'min_schools': 3}
    )
    
    # Verify Yelp was called
    mock_yelp_client.get_neighborhood_reviews.assert_called_once()
    
    # Verify vector store was called
    mock_vector_store.search_similar_neighborhoods.assert_called_once()
    
    # Verify result structure
    assert 'query' in result
    assert 'location' in result
    assert 'fit_score' in result
    assert 'forecast' in result
    assert 'eco_roi' in result
    assert 'review_insights' in result
    assert 'similar_neighborhoods' in result


@pytest.mark.asyncio
async def test_analyze_neighborhood_no_location(whisper_agent):
    """Test neighborhood analysis with unparseable location"""
    whisper_agent.nlp_chain.invoke = AsyncMock(return_value={
        'location': '',
        'zip_code': None
    })
    
    query = "I want a nice place"
    
    with pytest.raises(NeighborhoodSearchException):
        await whisper_agent.analyze_neighborhood(query=query)


@pytest.mark.asyncio
async def test_analyze_neighborhood_yelp_error(whisper_agent, mock_yelp_client):
    """Test handling of Yelp API errors"""
    mock_yelp_client.get_neighborhood_reviews = Mock(
        side_effect=Exception("Yelp API error")
    )
    
    query = "Seattle neighborhood"
    
    # Should handle error gracefully
    result = await whisper_agent.analyze_neighborhood(query=query)
    
    assert 'fit_score' in result
    # Should still return result even if Yelp fails


@pytest.mark.asyncio
async def test_analyze_neighborhood_vector_search_error(whisper_agent, mock_vector_store):
    """Test handling of vector search errors"""
    mock_vector_store.search_similar_neighborhoods = AsyncMock(
        side_effect=Exception("Pinecone error")
    )
    
    query = "Seattle neighborhood"
    
    # Should handle error gracefully
    result = await whisper_agent.analyze_neighborhood(query=query)
    
    assert 'fit_score' in result
    # Should still return result even if vector search fails


def test_calculate_amenities_score(whisper_agent, mock_yelp_client):
    """Test amenities score calculation"""
    reviews = [
        {
            'business_id': 'biz1',
            'name': 'Park',
            'reviews': [{'text': 'Great park', 'rating': 5}]
        },
        {
            'business_id': 'biz2',
            'name': 'School',
            'reviews': [{'text': 'Excellent school', 'rating': 5}]
        }
    ]
    
    parsed_query = {
        'amenities': ['parks', 'schools'],
        'lifestyle': ['family-friendly']
    }
    
    score = whisper_agent._calculate_amenities_score(reviews, parsed_query)
    
    assert isinstance(score, (int, float))
    assert 0 <= score <= 1


def test_calculate_eco_score(whisper_agent, mock_yelp_client):
    """Test eco score calculation"""
    reviews = [
        {
            'business_id': 'biz1',
            'name': 'Green Store',
            'reviews': [{'text': 'Eco-friendly', 'rating': 5}]
        }
    ]
    
    parsed_query = {
        'lifestyle': ['eco-friendly']
    }
    
    score = whisper_agent._calculate_eco_score(reviews, parsed_query)
    
    assert isinstance(score, (int, float))
    assert 0 <= score <= 1


def test_generate_forecast(whisper_agent):
    """Test forecast generation"""
    location = "Seattle, WA"
    fit_score = 82.5
    
    forecast = whisper_agent._generate_forecast(location, fit_score)
    
    assert isinstance(forecast, dict)
    assert 'trend' in forecast
    assert 'growth_rate' in forecast or 'growth_rate_12_months' in forecast


def test_calculate_eco_roi(whisper_agent):
    """Test eco ROI calculation"""
    eco_score = 0.75
    forecast = {
        'growth_rate_12_months': 0.05
    }
    
    roi = whisper_agent._calculate_eco_roi(eco_score, forecast)
    
    assert isinstance(roi, (int, float))
    assert roi >= 0

