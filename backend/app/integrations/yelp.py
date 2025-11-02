"""Yelp API integration for neighborhood reviews and sentiment"""
from typing import List, Dict, Any, Optional
import requests
import logging

from ..config import settings
from ..shared.exceptions import IntegrationException

logger = logging.getLogger(__name__)


class YelpIntegration:
    """
    Yelp API integration for fetching neighborhood reviews.
    
    Used by Neighborhood Whisper to analyze sentiment and get
    neighborhood insights from Yelp reviews.
    """
    
    def __init__(self):
        """Initialize Yelp client"""
        self.api_key = settings.YELP_API_KEY
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        } if self.api_key else {}
    
    def search_businesses(
        self,
        location: str,
        categories: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for businesses in a location.
        
        Args:
            location: Location string (address, city, zip)
            categories: Optional list of Yelp categories (e.g., ['restaurants', 'shopping'])
            limit: Maximum results to return
            
        Returns:
            List of business dictionaries
        """
        if not self.api_key:
            logger.warning("Yelp API key not configured")
            return []
        
        try:
            url = f"{self.base_url}/businesses/search"
            params = {
                "location": location,
                "limit": limit
            }
            
            if categories:
                params["categories"] = ",".join(categories)
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get("businesses", [])
            
        except Exception as e:
            logger.error(f"Yelp API error: {e}")
            raise IntegrationException(f"Failed to search Yelp businesses: {str(e)}")
    
    def get_business_reviews(
        self,
        business_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get reviews for a specific business.
        
        Args:
            business_id: Yelp business ID
            limit: Maximum reviews to return
            
        Returns:
            List of review dictionaries
        """
        if not self.api_key:
            logger.warning("Yelp API key not configured")
            return []
        
        try:
            url = f"{self.base_url}/businesses/{business_id}/reviews"
            params = {"limit": limit}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get("reviews", [])
            
        except Exception as e:
            logger.error(f"Yelp API error fetching reviews: {e}")
            raise IntegrationException(f"Failed to get Yelp reviews: {str(e)}")
    
    def get_neighborhood_reviews(
        self,
        location: str,
        max_businesses: int = 10,
        max_reviews_per_business: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get reviews from multiple businesses in a neighborhood.
        
        Args:
            location: Location string (address, city, zip)
            max_businesses: Maximum businesses to query
            max_reviews_per_business: Maximum reviews per business
            
        Returns:
            List of review dictionaries with business context
        """
        if not self.api_key:
            logger.warning("Yelp API key not configured")
            return []
        
        try:
            # Search for popular businesses in area
            businesses = self.search_businesses(
                location=location,
                categories=['restaurants', 'shopping', 'services'],
                limit=max_businesses
            )
            
            all_reviews = []
            for business in businesses:
                business_id = business.get("id")
                if not business_id:
                    continue
                
                reviews = self.get_business_reviews(business_id, limit=max_reviews_per_business)
                
                for review in reviews:
                    review['business'] = {
                        'name': business.get("name"),
                        'rating': business.get("rating"),
                        'categories': [cat.get("title") for cat in business.get("categories", [])]
                    }
                    all_reviews.append(review)
            
            return all_reviews
            
        except Exception as e:
            logger.error(f"Error fetching neighborhood reviews: {e}")
            return []
    
    def extract_sentiment_from_reviews(
        self,
        reviews: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract sentiment metrics from reviews.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dict with sentiment scores and insights
        """
        if not reviews:
            return {
                'average_rating': 0.0,
                'sentiment_score': 0.0,
                'total_reviews': 0,
                'positive_count': 0,
                'negative_count': 0,
                'common_themes': []
            }
        
        ratings = [review.get("rating", 0) for review in reviews]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Simple sentiment: positive (>4), neutral (3-4), negative (<3)
        positive_count = sum(1 for r in ratings if r >= 4)
        negative_count = sum(1 for r in ratings if r < 3)
        
        # Sentiment score (0-100 scale)
        sentiment_score = (average_rating / 5.0) * 100
        
        # Extract common themes from review text
        common_themes = []
        all_text = ' '.join([
            review.get("text", "").lower() for review in reviews[:10]  # Limit for performance
        ])
        
        theme_keywords = {
            'clean': ['clean', 'cleanliness', 'tidy'],
            'friendly': ['friendly', 'welcoming', 'nice'],
            'convenient': ['convenient', 'close', 'nearby', 'accessible'],
            'noisy': ['noisy', 'loud', 'sound'],
            'safe': ['safe', 'security', 'secure'],
            'affordable': ['affordable', 'cheap', 'reasonable']
        }
        
        for theme, keywords in theme_keywords.items():
            matches = sum(1 for kw in keywords if kw in all_text)
            if matches >= 2:
                common_themes.append(theme)
        
        return {
            'average_rating': round(average_rating, 2),
            'sentiment_score': round(sentiment_score, 2),
            'total_reviews': len(reviews),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'common_themes': common_themes
        }

