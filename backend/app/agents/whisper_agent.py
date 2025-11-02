"""Neighborhood Whisper Agent - NLP/ML for neighborhood fit scores"""
from typing import Dict, Any, List, Optional
import logging
from openai import OpenAI
import json

from ..config import settings
from ..integrations.yelp import YelpIntegration
from ..integrations.vector_store import VectorStore
from ..utils.ml_utils import calculate_fit_score, generate_simple_forecast
from ..shared.exceptions import NeighborhoodSearchException

logger = logging.getLogger(__name__)


class WhisperAgent:
    """
    Neighborhood Whisper agent for neighborhood analysis.
    
    Uses OpenAI GPT-4o-mini for NLP parsing, Yelp for reviews,
    Pinecone for vector search, and ML for scoring.
    """
    
    def __init__(
        self,
        openai_client: Optional[OpenAI] = None,
        yelp_client: Optional[YelpIntegration] = None,
        vector_store: Optional[VectorStore] = None
    ):
        """
        Initialize Whisper agent.
        
        Args:
            openai_client: Optional OpenAI client (for dependency injection)
            yelp_client: Optional Yelp client (for dependency injection)
            vector_store: Optional VectorStore client (for dependency injection)
        """
        self.openai_client = openai_client or OpenAI(api_key=settings.OPENAI_API_KEY)
        self.yelp_client = yelp_client or YelpIntegration()
        self.vector_store = vector_store or VectorStore()
        self.model = settings.OPENAI_MODEL
    
    async def analyze_neighborhood(
        self,
        query: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze neighborhood based on query.
        
        Args:
            query: Search query (e.g., "family-friendly neighborhood in Seattle")
            user_preferences: Optional user preferences dict
            
        Returns:
            Dict with fit score, forecast, and insights
        """
        try:
            # Step 1: Parse query with OpenAI NLP
            logger.info(f"Parsing query: {query}")
            parsed_query = await self._parse_query(query, user_preferences)
            
            location = parsed_query.get('location', '')
            zip_code = parsed_query.get('zip_code')
            
            if not location:
                raise NeighborhoodSearchException("Could not extract location from query")
            
            # Step 2: Fetch Yelp reviews
            logger.info(f"Fetching reviews for {location}...")
            reviews = self.yelp_client.get_neighborhood_reviews(
                location=location,
                max_businesses=10,
                max_reviews_per_business=5
            )
            
            # Step 3: Vectorize and search similar neighborhoods
            logger.info("Searching similar neighborhoods...")
            similar_neighborhoods = await self._search_similar_neighborhoods(
                query,
                location
            )
            
            # Step 4: Calculate sentiment and scores
            sentiment_data = self.yelp_client.extract_sentiment_from_reviews(reviews)
            
            # Step 5: Calculate fit score using ML
            amenities_score = self._calculate_amenities_score(reviews, parsed_query)
            sentiment_score = sentiment_data.get('sentiment_score', 0)
            eco_score = self._calculate_eco_score(reviews, parsed_query)
            
            fit_score = calculate_fit_score(
                amenities_score=amenities_score,
                sentiment_score=sentiment_score,
                eco_score=eco_score
            )
            
            # Step 6: Generate forecast
            forecast = self._generate_forecast(location, fit_score)
            
            # Step 7: Calculate eco ROI
            eco_roi = self._calculate_eco_roi(eco_score, forecast)
            
            return {
                'query': query,
                'location': location,
                'zip_code': zip_code,
                'fit_score': fit_score,
                'amenities_score': amenities_score,
                'sentiment_score': sentiment_score,
                'eco_score': eco_score,
                'forecast': forecast,
                'eco_roi': eco_roi,
                'review_insights': {
                    'average_rating': sentiment_data.get('average_rating'),
                    'total_reviews': sentiment_data.get('total_reviews'),
                    'common_themes': sentiment_data.get('common_themes'),
                    'sentiment_breakdown': {
                        'positive': sentiment_data.get('positive_count'),
                        'negative': sentiment_data.get('negative_count')
                    }
                },
                'similar_neighborhoods': similar_neighborhoods,
                'market_data': {
                    'location': location,
                    'fit_score': fit_score,
                    'trend': forecast.get('trend', 'stable')
                },
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Neighborhood analysis error: {e}")
            raise NeighborhoodSearchException(f"Failed to analyze neighborhood: {str(e)}")
    
    async def _parse_query(
        self,
        query: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Parse query using OpenAI to extract location and preferences"""
        try:
            system_prompt = """You are a real estate assistant. Parse the user's neighborhood query and extract:
1. Location (address, city, zip code, neighborhood name)
2. Preferences (family-friendly, walkable, quiet, etc.)
3. Property type interests (if mentioned)
4. Budget range (if mentioned)

Return JSON with keys: location, zip_code, preferences (array), property_types (array), budget_range (object with min/max).
"""
            
            user_prompt = f"Query: {query}\n\nUser preferences: {json.dumps(user_preferences or {})}"
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Query parsing error: {e}")
            # Fallback: try to extract location from query
            return {
                'location': query.split('in')[-1].strip() if 'in' in query else query,
                'zip_code': None,
                'preferences': [],
                'property_types': [],
                'budget_range': {}
            }
    
    async def _search_similar_neighborhoods(
        self,
        query: str,
        location: str
    ) -> List[Dict[str, Any]]:
        """Search for similar neighborhoods using vector embeddings"""
        try:
            # Generate embedding for query
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = response.data[0].embedding
            
            # Search Pinecone
            results = await self.vector_store.search_similar_neighborhoods(
                query_embedding=query_embedding,
                location=None,  # Search across all locations
                top_k=5
            )
            
            if results.get('success'):
                return results.get('matches', [])
            
            return []
            
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            return []
    
    def _calculate_amenities_score(
        self,
        reviews: List[Dict[str, Any]],
        parsed_query: Dict[str, Any]
    ) -> float:
        """Calculate amenities score based on reviews and preferences"""
        # Look for amenities mentioned in reviews
        all_text = ' '.join([
            review.get('text', '').lower() for review in reviews[:20]
        ])
        
        amenity_keywords = {
            'park': ['park', 'playground', 'outdoor'],
            'school': ['school', 'education', 'academic'],
            'shopping': ['shopping', 'store', 'mall', 'retail'],
            'restaurants': ['restaurant', 'dining', 'food', 'cafe'],
            'transportation': ['transit', 'bus', 'train', 'metro', 'walkable'],
            'safety': ['safe', 'security', 'secure']
        }
        
        preferences = [p.lower() for p in parsed_query.get('preferences', [])]
        
        score = 50.0  # Base score
        
        # Check if preferred amenities are mentioned
        for amenity, keywords in amenity_keywords.items():
            matches = sum(1 for kw in keywords if kw in all_text)
            if matches > 0:
                score += 5.0 * min(matches, 3)  # Up to +15 points per amenity
            
            # Bonus if it matches user preferences
            if any(p in amenity or amenity in p for p in preferences):
                score += 10.0
        
        return min(100.0, score)
    
    def _calculate_eco_score(
        self,
        reviews: List[Dict[str, Any]],
        parsed_query: Dict[str, Any]
    ) -> float:
        """Calculate eco-friendliness score"""
        all_text = ' '.join([
            review.get('text', '').lower() for review in reviews[:20]
        ])
        
        eco_keywords = {
            'positive': ['green', 'sustainable', 'eco-friendly', 'recycling', 'solar', 'bike', 'walkable'],
            'negative': ['pollution', 'traffic', 'noise', 'industrial']
        }
        
        positive_matches = sum(1 for kw in eco_keywords['positive'] if kw in all_text)
        negative_matches = sum(1 for kw in eco_keywords['negative'] if kw in all_text)
        
        score = 50.0  # Base score
        score += positive_matches * 5.0
        score -= negative_matches * 5.0
        
        return max(0.0, min(100.0, score))
    
    def _generate_forecast(
        self,
        location: str,
        fit_score: float
    ) -> Dict[str, Any]:
        """Generate market forecast"""
        # Simple forecast based on fit score
        # Higher fit score = positive growth
        growth_rate = (fit_score - 50) / 10  # Scale to -5% to +5%
        
        # Estimate current value (placeholder - would use real market data)
        current_value = 500000  # Base estimate
        
        return generate_simple_forecast(
            current_value=current_value,
            growth_rate=growth_rate,
            months=12
        )
    
    def _calculate_eco_roi(
        self,
        eco_score: float,
        forecast: Dict[str, Any]
    ) -> float:
        """Calculate ROI for eco investments"""
        # Higher eco score = better ROI potential
        # Base ROI assumption: eco improvements add 0.5-2% value
        roi_multiplier = eco_score / 100.0
        
        # Estimate ROI based on property value trend
        estimated_increase = forecast.get('predictions', [{}])[-1].get('value', 500000) - forecast.get('current_value', 500000)
        eco_roi = estimated_increase * 0.01 * roi_multiplier  # 1% of value increase
        
        return round(eco_roi, 2)

