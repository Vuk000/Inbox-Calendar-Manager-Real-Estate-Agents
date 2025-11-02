"""ML utilities for fit score calculation and property matching"""
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


def calculate_fit_score(
    amenities_score: float,
    sentiment_score: float,
    eco_score: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate neighborhood fit score using weighted combination.
    
    Formula: fit_score = 0.5*amenities + 0.3*sentiment + 0.2*eco
    
    Args:
        amenities_score: Score for amenities (0-100)
        sentiment_score: Score from reviews sentiment (0-100)
        eco_score: Environmental/eco-friendliness score (0-100)
        weights: Optional custom weights dict with keys: 'amenities', 'sentiment', 'eco'
        
    Returns:
        Fit score (0-100)
    """
    if weights is None:
        weights = {
            'amenities': 0.5,
            'sentiment': 0.3,
            'eco': 0.2
        }
    
    # Normalize scores to 0-100 range
    amenities_norm = max(0, min(100, amenities_score))
    sentiment_norm = max(0, min(100, sentiment_score))
    eco_norm = max(0, min(100, eco_score))
    
    # Calculate weighted score
    fit_score = (
        weights['amenities'] * amenities_norm +
        weights['sentiment'] * sentiment_norm +
        weights['eco'] * eco_norm
    )
    
    return round(fit_score, 2)


def match_properties_kmeans(
    property_features: List[Dict[str, Any]],
    target_features: Dict[str, Any],
    n_clusters: int = 5,
    max_matches: int = 10
) -> List[Dict[str, Any]]:
    """
    Match similar properties using KMeans clustering.
    
    Args:
        property_features: List of property feature dicts with keys like:
            {'price': float, 'bedrooms': int, 'bathrooms': float, 'sqft': int, ...}
        target_features: Target property features to match against
        n_clusters: Number of clusters for KMeans
        max_matches: Maximum number of matches to return
        
    Returns:
        List of matched properties with similarity scores
    """
    if not property_features:
        return []
    
    try:
        # Extract feature vectors
        feature_keys = ['price', 'bedrooms', 'bathrooms', 'sqft']
        
        # Build feature matrix
        X = []
        property_indices = []
        for idx, prop in enumerate(property_features):
            features = []
            for key in feature_keys:
                value = prop.get(key, 0)
                if isinstance(value, (int, float)):
                    features.append(float(value))
                else:
                    features.append(0.0)
            X.append(features)
            property_indices.append(idx)
        
        if len(X) < n_clusters:
            n_clusters = len(X)
        
        if not X:
            return []
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Fit KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Build target feature vector
        target_vector = []
        for key in feature_keys:
            value = target_features.get(key, 0)
            if isinstance(value, (int, float)):
                target_vector.append(float(value))
            else:
                target_vector.append(0.0)
        
        target_scaled = scaler.transform([target_vector])[0]
        
        # Find closest cluster
        target_cluster = kmeans.predict([target_scaled])[0]
        
        # Get properties in same cluster
        cluster_indices = [i for i, c in enumerate(clusters) if c == target_cluster]
        
        # Calculate cosine similarity for ranking
        matches = []
        for idx in cluster_indices:
            prop = property_features[idx]
            prop_vector = X_scaled[idx]
            similarity = cosine_similarity([target_scaled], [prop_vector])[0][0]
            
            matches.append({
                'property': prop,
                'similarity_score': float(similarity),
                'cluster': int(clusters[idx])
            })
        
        # Sort by similarity and return top matches
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches[:max_matches]
        
    except Exception as e:
        logger.error(f"Error in property matching: {e}")
        # Fallback: simple distance-based matching
        return _simple_distance_match(property_features, target_features, max_matches)


def _simple_distance_match(
    property_features: List[Dict[str, Any]],
    target_features: Dict[str, Any],
    max_matches: int = 10
) -> List[Dict[str, Any]]:
    """Fallback simple distance-based matching"""
    matches = []
    
    for prop in property_features:
        score = 0.0
        total_weight = 0.0
        
        # Price similarity (inverse distance)
        if 'price' in prop and 'price' in target_features:
            price_diff = abs(prop['price'] - target_features['price'])
            price_score = 1.0 / (1.0 + price_diff / 100000)  # Normalize by $100k
            score += price_score * 0.4
            total_weight += 0.4
        
        # Bedrooms similarity
        if 'bedrooms' in prop and 'bedrooms' in target_features:
            bed_diff = abs(prop['bedrooms'] - target_features['bedrooms'])
            bed_score = 1.0 / (1.0 + bed_diff)
            score += bed_score * 0.2
            total_weight += 0.2
        
        # Bathrooms similarity
        if 'bathrooms' in prop and 'bathrooms' in target_features:
            bath_diff = abs(prop['bathrooms'] - target_features['bathrooms'])
            bath_score = 1.0 / (1.0 + bath_diff)
            score += bath_score * 0.2
            total_weight += 0.2
        
        # Square feet similarity
        if 'sqft' in prop and 'sqft' in target_features:
            sqft_diff = abs(prop['sqft'] - target_features['sqft'])
            sqft_score = 1.0 / (1.0 + sqft_diff / 1000)  # Normalize by 1000 sqft
            score += sqft_score * 0.2
            total_weight += 0.2
        
        if total_weight > 0:
            normalized_score = score / total_weight
            matches.append({
                'property': prop,
                'similarity_score': normalized_score
            })
    
    matches.sort(key=lambda x: x['similarity_score'], reverse=True)
    return matches[:max_matches]


def generate_simple_forecast(
    current_value: float,
    growth_rate: float,
    months: int = 12
) -> Dict[str, Any]:
    """
    Generate simple forecast using linear regression.
    
    Args:
        current_value: Current property value or metric
        growth_rate: Annual growth rate (e.g., 5.2 for 5.2%)
        months: Number of months to forecast
        
    Returns:
        Forecast dict with predictions
    """
    monthly_rate = growth_rate / 12.0 / 100.0
    
    predictions = []
    for month in range(1, months + 1):
        predicted_value = current_value * (1 + monthly_rate * month)
        predictions.append({
            'month': month,
            'value': round(predicted_value, 2),
            'growth': round(monthly_rate * month * 100, 2)
        })
    
    return {
        'current_value': current_value,
        'growth_rate': growth_rate,
        'forecast_months': months,
        'predictions': predictions,
        'trend': 'up' if growth_rate > 0 else 'down' if growth_rate < 0 else 'stable'
    }

