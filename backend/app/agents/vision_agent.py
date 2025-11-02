"""VisionHome AI Agent - Computer vision analysis for property scans"""
from typing import Dict, Any, List, Optional
import logging
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..config import settings
from ..integrations.google_vision import GoogleVisionClient
from ..integrations.zillow_integration import ZillowIntegration, PropertyComp
from ..utils.ml_utils import match_properties_kmeans
from ..shared.exceptions import VisionProcessingException

logger = logging.getLogger(__name__)


class VisionAgent:
    """
    VisionHome AI agent for property image analysis.
    
    Uses Google Cloud Vision for image analysis and LangChain for
    intelligent processing, then matches properties using ML.
    """
    
    def __init__(
        self,
        vision_client: Optional[GoogleVisionClient] = None,
        zillow_client: Optional[ZillowIntegration] = None,
        llm_client: Optional[Any] = None
    ):
        """
        Initialize Vision agent.
        
        Args:
            vision_client: Optional Google Vision client (for dependency injection)
            zillow_client: Optional Zillow client (for dependency injection)
            llm_client: Optional LLM client (uses Anthropic Claude by default)
        """
        self.vision_client = vision_client or GoogleVisionClient()
        self.zillow_client = zillow_client or ZillowIntegration()
        
        # Initialize LLM (use Claude for analysis)
        if llm_client:
            self.llm = llm_client
        else:
            self.llm = ChatAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.ANTHROPIC_MODEL,
                temperature=0.3
            )
        
        # LangChain prompt for property analysis
        self.analysis_prompt = PromptTemplate(
            input_variables=["vision_labels", "rooms", "features"],
            template="""
            Analyze this property image data and provide insights:
            
            Detected Labels: {vision_labels}
            Rooms Detected: {rooms}
            Property Features: {features}
            
            Provide:
            1. Property type assessment (house, condo, apartment, etc.)
            2. Condition assessment (excellent, good, fair, needs work)
            3. Key selling points
            4. Renovation opportunities
            5. Estimated property value range
            
            Format as JSON with keys: property_type, condition, selling_points (array), 
            renovation_opportunities (array), estimated_value_range (object with min/max).
            """
        )
        
        self.analysis_chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
    
    async def analyze_property_image(
        self,
        image_content: bytes,
        image_uri: Optional[str] = None,
        property_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze property image and generate insights.
        
        Args:
            image_content: Image bytes (if provided)
            image_uri: Image URI (if provided)
            property_address: Optional property address for Zillow matching
            
        Returns:
            Dict with analysis results, matches, and renovations
        """
        try:
            # Step 1: Google Vision analysis
            logger.info("Starting Google Vision analysis...")
            vision_results = self.vision_client.analyze_image(
                image_content=image_content,
                image_uri=image_uri
            )
            
            # Step 2: LLM analysis for insights
            logger.info("Running LLM analysis...")
            labels_text = ", ".join([l['description'] for l in vision_results.get('labels', [])[:10]])
            rooms_text = ", ".join([r['type'] for r in vision_results.get('rooms', [])])
            features_text = str(vision_results.get('property_features', {}))
            
            analysis_result = await self.analysis_chain.arun(
                vision_labels=labels_text,
                rooms=rooms_text,
                features=features_text
            )
            
            # Parse LLM response (should be JSON)
            import json
            try:
                analysis_data = json.loads(analysis_result)
            except:
                # Fallback if not valid JSON
                analysis_data = {
                    "property_type": vision_results.get('property_features', {}).get('style', 'unknown'),
                    "condition": vision_results.get('property_features', {}).get('condition', 'unknown'),
                    "selling_points": [],
                    "renovation_opportunities": vision_results.get('property_features', {}).get('renovation_opportunities', []),
                    "estimated_value_range": {"min": 0, "max": 0}
                }
            
            # Step 3: Find similar properties using Zillow and ML
            matches = []
            if property_address:
                logger.info(f"Finding similar properties for {property_address}...")
                try:
                    comps = await self.zillow_client.get_comps(
                        address=property_address,
                        radius_miles=0.5,
                        max_results=20
                    )
                    
                    if comps:
                        # Extract features from vision analysis for matching
                        target_features = self._extract_matching_features(vision_results, analysis_data)
                        
                        # Convert comps to feature dicts
                        comp_features = [
                            {
                                'price': comp.price,
                                'bedrooms': comp.bedrooms,
                                'bathrooms': comp.bathrooms,
                                'sqft': comp.square_feet,
                                'address': comp.address
                            }
                            for comp in comps
                        ]
                        
                        # Use ML matching
                        matched = match_properties_kmeans(
                            property_features=comp_features,
                            target_features=target_features,
                            n_clusters=5,
                            max_matches=10
                        )
                        
                        matches = [
                            {
                                'property': match['property'],
                                'similarity_score': round(match['similarity_score'], 3)
                            }
                            for match in matched
                        ]
                except Exception as e:
                    logger.warning(f"Property matching failed: {e}")
            
            # Step 4: Generate renovation suggestions
            renovations = self._generate_renovation_suggestions(
                vision_results,
                analysis_data,
                matches
            )
            
            return {
                'vision_labels': vision_results.get('labels', []),
                'rooms_detected': vision_results.get('rooms', []),
                'property_features': vision_results.get('property_features', {}),
                'analysis': analysis_data,
                'matches': matches,
                'renovations': renovations,
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            raise VisionProcessingException(f"Failed to analyze property image: {str(e)}")
    
    def _extract_matching_features(
        self,
        vision_results: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract features for property matching"""
        # Estimate bedrooms/bathrooms from rooms detected
        rooms = vision_results.get('rooms', [])
        bedrooms = sum(1 for r in rooms if 'bedroom' in r.get('type', '').lower())
        bathrooms = sum(1 for r in rooms if 'bathroom' in r.get('type', '').lower())
        
        # Estimate square footage from room count (rough estimate)
        estimated_sqft = (bedrooms + bathrooms + len(rooms)) * 300  # Rough estimate
        
        return {
            'bedrooms': max(1, bedrooms),
            'bathrooms': max(1, bathrooms),
            'sqft': estimated_sqft,
            'price': analysis_data.get('estimated_value_range', {}).get('max', 500000)
        }
    
    def _generate_renovation_suggestions(
        self,
        vision_results: Dict[str, Any],
        analysis_data: Dict[str, Any],
        matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate renovation suggestions with overlays"""
        renovations = {
            'suggestions': [],
            'estimated_cost': {},
            'roi_estimate': {}
        }
        
        # Get renovation opportunities from analysis
        opportunities = analysis_data.get('renovation_opportunities', [])
        property_features = vision_results.get('property_features', {})
        
        renovation_map = {
            'kitchen_update': {
                'name': 'Kitchen Update',
                'description': 'Modernize kitchen with new cabinets, countertops, and appliances',
                'estimated_cost': 15000,
                'roi': 0.80
            },
            'bathroom_remodel': {
                'name': 'Bathroom Remodel',
                'description': 'Update bathroom fixtures, tiles, and lighting',
                'estimated_cost': 10000,
                'roi': 0.70
            },
            'flooring_refresh': {
                'name': 'Flooring Refresh',
                'description': 'Replace or refinish flooring throughout',
                'estimated_cost': 8000,
                'roi': 0.75
            },
            'paint_update': {
                'name': 'Paint Update',
                'description': 'Fresh paint inside and out',
                'estimated_cost': 3000,
                'roi': 1.20
            }
        }
        
        for opp in opportunities:
            if opp in renovation_map:
                renovation = renovation_map[opp]
                renovations['suggestions'].append({
                    'type': opp,
                    'name': renovation['name'],
                    'description': renovation['description'],
                    'estimated_cost': renovation['estimated_cost'],
                    'roi_multiplier': renovation['roi'],
                    'rooms': [r['type'] for r in vision_results.get('rooms', []) if opp in r.get('type', '').lower()]
                })
        
        # Calculate total estimated cost
        total_cost = sum(s['estimated_cost'] for s in renovations['suggestions'])
        renovations['estimated_cost']['total'] = total_cost
        renovations['estimated_cost']['breakdown'] = {
            s['type']: s['estimated_cost'] for s in renovations['suggestions']
        }
        
        # Estimate ROI based on matches
        if matches:
            avg_price = sum(m['property'].get('price', 0) for m in matches) / len(matches)
            renovations['roi_estimate'] = {
                'investment': total_cost,
                'potential_value_increase': total_cost * 0.8,  # Average ROI
                'estimated_new_value': avg_price + (total_cost * 0.8)
            }
        
        return renovations

