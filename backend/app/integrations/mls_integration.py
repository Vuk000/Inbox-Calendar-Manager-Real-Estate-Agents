"""
MLS and Zillow API integration for property data
"""
from typing import Dict, Any, List, Optional
import requests
from ..config import settings


class MLSIntegration:
    """
    MLS and Zillow integration for property data and comparables.
    """
    
    def __init__(self):
        self.zillow_api_key = settings.ZILLOW_API_KEY
        self.rapidapi_key = settings.RAPIDAPI_KEY
        self.zillow_base_url = "https://zillow-com1.p.rapidapi.com"
    
    async def get_property_details(
        self,
        address: str,
        city: Optional[str] = None,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get property details from Zillow.
        
        Args:
            address: Property address
            city: City name
            state: State code (e.g., "CA")
            
        Returns:
            Property details
        """
        try:
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
            }
            
            params = {
                "address": address,
                "city": city or "",
                "state": state or ""
            }
            
            response = requests.get(
                f"{self.zillow_base_url}/property",
                headers=headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "property": data,
                "address": address
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    async def get_comparables(
        self,
        address: str,
        radius_miles: float = 0.5,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Get comparable properties (comps) for pricing analysis.
        
        Args:
            address: Subject property address
            radius_miles: Search radius in miles
            max_results: Maximum number of comps to return
            
        Returns:
            List of comparable properties
        """
        try:
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
            }
            
            params = {
                "address": address,
                "radius": radius_miles,
                "limit": max_results
            }
            
            response = requests.get(
                f"{self.zillow_base_url}/comps",
                headers=headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse comps
            comps = []
            for comp in data.get("properties", [])[:max_results]:
                comps.append({
                    "address": comp.get("address"),
                    "sale_price": comp.get("price"),
                    "bedrooms": comp.get("bedrooms"),
                    "bathrooms": comp.get("bathrooms"),
                    "square_feet": comp.get("livingArea"),
                    "sale_date": comp.get("dateSold"),
                    "distance_miles": comp.get("distance")
                })
            
            return {
                "success": True,
                "comps": comps,
                "count": len(comps),
                "subject_address": address
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "comps": []
            }
    
    async def get_market_trends(
        self,
        city: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Get market trends for an area.
        
        Args:
            city: City name
            state: State code
            
        Returns:
            Market trend data
        """
        try:
            # Simplified - would use actual MLS API
            return {
                "success": True,
                "city": city,
                "state": state,
                "trend": "stable",  # rising, falling, stable
                "median_price": 0,
                "avg_days_on_market": 0,
                "inventory": 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

