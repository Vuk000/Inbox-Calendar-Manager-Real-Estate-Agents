"""
Google Calendar integration - OAuth and event management
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..config import settings
from ..security.encryption import encrypt_data, decrypt_data


class GoogleCalendarIntegration:
    """
    Google Calendar integration for scheduling real estate activities.
    Handles OAuth and calendar event management.
    """
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
    
    def get_authorization_url(self, state: str = None) -> str:
        """Generate OAuth authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )
        
        return auth_url
    
    async def create_showing_event(
        self,
        encrypted_access_token: str,
        property_address: str,
        start_time: datetime,
        duration_minutes: int = 60,
        client_email: Optional[str] = None,
        notes: Optional[str] = None,
        encrypted_refresh_token: str = None
    ) -> Dict[str, Any]:
        """
        Create a property showing event in calendar.
        
        Args:
            encrypted_access_token: Encrypted OAuth token
            property_address: Property address
            start_time: Showing start time
            duration_minutes: Duration in minutes
            client_email: Client's email for calendar invite
            notes: Additional notes
            encrypted_refresh_token: Encrypted refresh token
            
        Returns:
            Created event data
        """
        from ..services.calendar_service import CalendarService
        
        calendar = CalendarService()
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        description = f"""Property Showing
Address: {property_address}

{notes or ''}

Checklist:
☐ Arrive 10 minutes early
☐ Turn on all lights
☐ Review property highlights
☐ Prepare comparable sales data
☐ Follow up within 24 hours
"""
        
        attendees = [client_email] if client_email else []
        
        return await calendar.create_event(
            encrypted_access_token=encrypted_access_token,
            title=f"Property Showing - {property_address}",
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=property_address,
            attendees=attendees,
            encrypted_refresh_token=encrypted_refresh_token
        )

