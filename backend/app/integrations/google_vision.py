"""Google Cloud Vision integration for VisionHome AI"""
from typing import List, Dict, Any, Optional
import os
import logging

# Optional Google Cloud Vision imports
try:
    from google.cloud import vision
    from google.oauth2 import service_account
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    vision = None
    service_account = None

from ..config import settings
from ..shared.exceptions import GoogleAPIException, VisionProcessingException

logger = logging.getLogger(__name__)


class GoogleVisionClient:
    """
    Google Cloud Vision API client for property image analysis.
    
    Detects rooms, objects, labels, and provides detailed image analysis
    for VisionHome AI feature.
    """
    
    def __init__(self):
        """Initialize Google Vision client"""
        if not GOOGLE_VISION_AVAILABLE:
            logger.warning(
                "Google Cloud Vision library not installed. "
                "Install with: pip install google-cloud-vision"
            )
            self.client = None
            return
            
        self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        
        if not self.credentials_path or not os.path.exists(self.credentials_path):
            logger.warning(
                "Google Cloud Vision credentials not found. "
                "Set GOOGLE_APPLICATION_CREDENTIALS environment variable."
            )
            self.client = None
            return
        
        try:
            # Load credentials from service account JSON
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            self.client = vision.ImageAnnotatorClient(credentials=credentials)
            logger.info("Google Cloud Vision client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Vision client: {e}")
            self.client = None
    
    def analyze_image(
        self,
        image_content: bytes,
        image_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze image using Google Cloud Vision API.
        
        Args:
            image_content: Image bytes (if provided)
            image_uri: Image URI (gs:// or https://) (if provided)
            
        Returns:
            Dict with analysis results including labels, objects, rooms, etc.
        """
        if not self.client:
            raise VisionProcessingException(
                "Google Cloud Vision not configured. "
                "Set GOOGLE_APPLICATION_CREDENTIALS environment variable."
            )
        
        try:
            # Create image object
            if image_content:
                image = vision.Image(content=image_content)
            elif image_uri:
                image = vision.Image()
                image.source.image_uri = image_uri
            else:
                raise VisionProcessingException("Either image_content or image_uri must be provided")
            
            # Perform various detections
            results = {}
            
            # Label detection (general labels)
            labels_response = self.client.label_detection(image=image)
            results['labels'] = [
                {
                    'description': label.description,
                    'score': label.score,
                    'mid': label.mid  # Google Knowledge Graph ID
                }
                for label in labels_response.label_annotations
            ]
            
            # Object detection (specific objects)
            objects_response = self.client.object_localization(image=image)
            results['objects'] = [
                {
                    'name': obj.name,
                    'score': obj.score,
                    'bounding_poly': [
                        {
                            'x': vertex.x,
                            'y': vertex.y
                        }
                        for vertex in obj.bounding_poly.normalized_vertices
                    ]
                }
                for obj in objects_response.localized_object_annotations
            ]
            
            # Text detection (OCR)
            text_response = self.client.text_detection(image=image)
            if text_response.text_annotations:
                results['text'] = {
                    'full_text': text_response.text_annotations[0].description,
                    'detections': [
                        {
                            'description': annotation.description,
                            'bounding_poly': [
                                {
                                    'x': vertex.x,
                                    'y': vertex.y
                                }
                                for vertex in annotation.bounding_poly.vertices
                            ]
                        }
                        for annotation in text_response.text_annotations[1:]  # Skip full text
                    ]
                }
            
            # Detect rooms and property features
            results['rooms'] = self._detect_rooms(results['labels'], results['objects'])
            results['property_features'] = self._extract_property_features(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Google Vision API error: {e}")
            raise VisionProcessingException(f"Failed to analyze image: {str(e)}")
    
    def _detect_rooms(
        self,
        labels: List[Dict[str, Any]],
        objects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect rooms based on labels and objects.
        
        Args:
            labels: Label detections
            objects: Object detections
            
        Returns:
            List of detected rooms
        """
        room_keywords = {
            'kitchen': ['kitchen', 'refrigerator', 'oven', 'stove', 'sink', 'cabinet'],
            'bedroom': ['bed', 'bedroom', 'mattress', 'pillow'],
            'bathroom': ['bathroom', 'toilet', 'sink', 'shower', 'bathtub'],
            'living_room': ['sofa', 'couch', 'television', 'tv', 'fireplace', 'living room'],
            'dining_room': ['dining', 'table', 'chair', 'dining room'],
            'office': ['desk', 'office', 'computer', 'monitor'],
            'garage': ['garage', 'car', 'vehicle']
        }
        
        detected_rooms = []
        
        # Check labels and objects for room indicators
        all_text = ' '.join([
            label['description'].lower() for label in labels
        ] + [
            obj['name'].lower() for obj in objects
        ])
        
        for room_type, keywords in room_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in all_text)
            if matches >= 2:  # At least 2 keywords match
                detected_rooms.append({
                    'type': room_type,
                    'confidence': min(0.9, matches / len(keywords)),
                    'indicators': [kw for kw in keywords if kw in all_text]
                })
        
        return detected_rooms
    
    def _extract_property_features(
        self,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract property-specific features from analysis.
        
        Args:
            analysis_results: Full analysis results
            
        Returns:
            Dict with property features
        """
        features = {
            'style': None,
            'condition': None,
            'amenities': [],
            'renovation_opportunities': []
        }
        
        # Detect style from labels
        style_keywords = {
            'modern': ['modern', 'contemporary', 'minimalist', 'sleek'],
            'traditional': ['traditional', 'classic', 'vintage', 'antique'],
            'rustic': ['rustic', 'wood', 'stone', 'country'],
            'luxury': ['luxury', 'premium', 'high-end', 'elegant']
        }
        
        all_labels = ' '.join([label['description'].lower() for label in analysis_results.get('labels', [])])
        
        for style, keywords in style_keywords.items():
            if any(kw in all_labels for kw in keywords):
                features['style'] = style
                break
        
        # Detect condition indicators
        condition_indicators = {
            'excellent': ['new', 'renovated', 'updated', 'refurbished'],
            'good': ['well-maintained', 'clean', 'maintained'],
            'fair': ['needs', 'repair', 'update', 'renovation']
        }
        
        for condition, keywords in condition_indicators.items():
            if any(kw in all_labels for kw in keywords):
                features['condition'] = condition
                break
        
        # Extract amenities
        amenity_keywords = ['pool', 'fireplace', 'patio', 'deck', 'balcony', 'garage', 'garden']
        features['amenities'] = [
            amenity for amenity in amenity_keywords
            if amenity in all_labels
        ]
        
        # Suggest renovation opportunities
        if features['condition'] == 'fair':
            features['renovation_opportunities'] = [
                'kitchen_update',
                'bathroom_remodel',
                'flooring_refresh',
                'paint_update'
            ]
        
        return features

