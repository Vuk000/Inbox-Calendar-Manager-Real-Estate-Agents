"""
CRM integration service - HubSpot and Zoho
"""
from typing import Dict, Any, Optional
from datetime import datetime
import requests
from ..config import settings


class CRMService:
    """
    CRM integrations for syncing leads and activities.
    Supports HubSpot and Zoho CRM.
    """
    
    def __init__(self, provider: str = "hubspot"):
        self.provider = provider
        
        if provider == "hubspot":
            self.api_key = settings.HUBSPOT_API_KEY
            self.base_url = "https://api.hubapi.com"
        elif provider == "zoho":
            self.client_id = settings.ZOHO_CLIENT_ID
            self.client_secret = settings.ZOHO_CLIENT_SECRET
            self.base_url = "https://www.zohoapis.com/crm/v2"
    
    async def create_contact(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        lead_score: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a contact in CRM.
        
        Args:
            email: Contact email
            first_name: First name
            last_name: Last name
            phone: Phone number
            lead_score: Lead qualification score (0-100)
            metadata: Additional properties
            
        Returns:
            Created contact data
        """
        if self.provider == "hubspot":
            return await self._create_hubspot_contact(
                email, first_name, last_name, phone, lead_score, metadata
            )
        elif self.provider == "zoho":
            return await self._create_zoho_contact(
                email, first_name, last_name, phone, lead_score, metadata
            )
    
    async def _create_hubspot_contact(
        self,
        email: str,
        first_name: Optional[str],
        last_name: Optional[str],
        phone: Optional[str],
        lead_score: Optional[int],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create contact in HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts"
            
            properties = {
                "email": email,
            }
            
            if first_name:
                properties["firstname"] = first_name
            if last_name:
                properties["lastname"] = last_name
            if phone:
                properties["phone"] = phone
            if lead_score is not None:
                properties["hs_lead_score"] = lead_score
            
            # Add custom properties from metadata
            if metadata:
                for key, value in metadata.items():
                    properties[key] = value
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                url,
                json={"properties": properties},
                headers=headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "contact_id": data.get("id"),
                "crm": "hubspot"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "crm": "hubspot"
            }
    
    async def _create_zoho_contact(
        self,
        email: str,
        first_name: Optional[str],
        last_name: Optional[str],
        phone: Optional[str],
        lead_score: Optional[int],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create contact in Zoho CRM"""
        # Simplified - would need OAuth token management
        return {
            "success": False,
            "error": "Zoho integration requires OAuth setup",
            "crm": "zoho"
        }
    
    async def log_activity(
        self,
        contact_email: str,
        activity_type: str,
        subject: str,
        body: str,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """
        Log an activity (email, call, meeting) in CRM.
        
        Args:
            contact_email: Contact email
            activity_type: Type (email, call, meeting)
            subject: Activity subject
            body: Activity details
            timestamp: When it occurred
            
        Returns:
            Log result
        """
        if self.provider == "hubspot":
            return await self._log_hubspot_activity(
                contact_email, activity_type, subject, body, timestamp
            )
        
        return {"success": False, "error": "CRM provider not supported"}
    
    async def _log_hubspot_activity(
        self,
        contact_email: str,
        activity_type: str,
        subject: str,
        body: str,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Log activity in HubSpot"""
        try:
            # First, find contact by email
            search_url = f"{self.base_url}/crm/v3/objects/contacts/search"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            search_data = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": contact_email
                    }]
                }]
            }
            
            search_response = requests.post(search_url, json=search_data, headers=headers)
            search_response.raise_for_status()
            
            results = search_response.json().get("results", [])
            
            if not results:
                return {"success": False, "error": "Contact not found"}
            
            contact_id = results[0].get("id")
            
            # Create engagement (email activity)
            engagement_url = f"{self.base_url}/crm/v3/objects/emails"
            
            engagement_data = {
                "properties": {
                    "hs_timestamp": timestamp.isoformat(),
                    "hubspot_owner_id": "",  # Would need owner mapping
                    "hs_email_subject": subject,
                    "hs_email_text": body[:5000],  # Limit to 5000 chars
                }
            }
            
            engagement_response = requests.post(
                engagement_url,
                json=engagement_data,
                headers=headers
            )
            
            engagement_response.raise_for_status()
            
            return {
                "success": True,
                "activity_id": engagement_response.json().get("id"),
                "contact_id": contact_id
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_deal_stage(
        self,
        deal_id: str,
        new_stage: str
    ) -> Dict[str, Any]:
        """
        Update deal pipeline stage.
        
        Args:
            deal_id: CRM deal ID
            new_stage: New stage (e.g., "qualified", "contract", "closing")
            
        Returns:
            Update result
        """
        if self.provider == "hubspot":
            try:
                url = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "properties": {
                        "dealstage": new_stage
                    }
                }
                
                response = requests.patch(url, json=data, headers=headers)
                response.raise_for_status()
                
                return {"success": True, "deal_id": deal_id}
                
            except requests.exceptions.RequestException as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Provider not supported"}

