"""
Google Calendar integration service
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..config import settings
from ..security.encryption import decrypt_data


class CalendarService:
    """
    Google Calendar integration for scheduling and event management.
    """
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.scopes = ['https://www.googleapis.com/auth/calendar']
    
    def _build_service(self, encrypted_access_token: str, encrypted_refresh_token: str = None):
        """Build Calendar API service"""
        access_token = decrypt_data(encrypted_access_token)
        refresh_token = decrypt_data(encrypted_refresh_token) if encrypted_refresh_token else None
        
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.scopes
        )
        
        return build('calendar', 'v3', credentials=credentials)
    
    async def create_event(
        self,
        encrypted_access_token: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        encrypted_refresh_token: str = None
    ) -> Dict[str, Any]:
        """
        Create a calendar event.
        
        Args:
            encrypted_access_token: Encrypted OAuth access token
            title: Event title
            start_time: Event start datetime
            end_time: Event end datetime
            description: Event description
            location: Event location (property address)
            attendees: List of attendee emails
            encrypted_refresh_token: Encrypted refresh token
            
        Returns:
            Created event data
        """
        try:
            service = self._build_service(encrypted_access_token, encrypted_refresh_token)
            
            event = {
                'summary': title,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 24 * 60},  # 24 hours
                        {'method': 'popup', 'minutes': 60},  # 1 hour
                    ],
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'  # Send notifications to attendees
            ).execute()
            
            return {
                "success": True,
                "event_id": created_event.get('id'),
                "event_link": created_event.get('htmlLink'),
                "start_time": created_event.get('start', {}).get('dateTime')
            }
            
        except HttpError as error:
            return {
                "success": False,
                "error": str(error)
            }
    
    async def list_events(
        self,
        encrypted_access_token: str,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 10,
        encrypted_refresh_token: str = None
    ) -> Dict[str, Any]:
        """
        List calendar events.
        
        Args:
            encrypted_access_token: Encrypted access token
            time_min: Minimum time for events
            time_max: Maximum time for events
            max_results: Maximum number of events
            encrypted_refresh_token: Encrypted refresh token
            
        Returns:
            List of events
        """
        try:
            service = self._build_service(encrypted_access_token, encrypted_refresh_token)
            
            if not time_min:
                time_min = datetime.utcnow()
            if not time_max:
                time_max = datetime.utcnow() + timedelta(days=30)
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return {
                "success": True,
                "events": events,
                "count": len(events)
            }
            
        except HttpError as error:
            return {
                "success": False,
                "error": str(error),
                "events": []
            }
    
    async def check_availability(
        self,
        encrypted_access_token: str,
        start_time: datetime,
        end_time: datetime,
        encrypted_refresh_token: str = None
    ) -> bool:
        """
        Check if time slot is available (no conflicts).
        
        Args:
            encrypted_access_token: Encrypted access token
            start_time: Proposed start time
            end_time: Proposed end time
            encrypted_refresh_token: Encrypted refresh token
            
        Returns:
            True if available, False if conflict exists
        """
        try:
            service = self._build_service(encrypted_access_token, encrypted_refresh_token)
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True
            ).execute()
            
            events = events_result.get('items', [])
            
            # No events = available
            return len(events) == 0
            
        except HttpError:
            # If error, assume not available to be safe
            return False
    
    async def update_event(
        self,
        encrypted_access_token: str,
        event_id: str,
        updates: Dict[str, Any],
        encrypted_refresh_token: str = None
    ) -> Dict[str, Any]:
        """
        Update an existing calendar event.
        
        Args:
            encrypted_access_token: Encrypted access token
            event_id: Event ID to update
            updates: Fields to update
            encrypted_refresh_token: Encrypted refresh token
            
        Returns:
            Updated event data
        """
        try:
            service = self._build_service(encrypted_access_token, encrypted_refresh_token)
            
            # Get existing event
            event = service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Apply updates
            event.update(updates)
            
            # Update event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                "success": True,
                "event_id": updated_event.get('id'),
                "updated_at": updated_event.get('updated')
            }
            
        except HttpError as error:
            return {
                "success": False,
                "error": str(error)
            }
    
    async def delete_event(
        self,
        encrypted_access_token: str,
        event_id: str,
        encrypted_refresh_token: str = None
    ) -> Dict[str, Any]:
        """Delete a calendar event"""
        try:
            service = self._build_service(encrypted_access_token, encrypted_refresh_token)
            
            service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            return {"success": True, "event_id": event_id}
            
        except HttpError as error:
            return {"success": False, "error": str(error)}

