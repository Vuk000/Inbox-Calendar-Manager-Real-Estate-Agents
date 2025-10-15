"""
Gmail Integration - OAuth, read, send, modify emails
Uses Google API Python Client
"""
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from datetime import datetime

from ..config import settings
from ..security.encryption import encrypt_data, decrypt_data


class GmailIntegration:
    """
    Gmail integration for reading, sending, and managing emails.
    Handles OAuth authentication and API calls.
    """
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.labels'
        ]
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate OAuth authorization URL for user consent.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL to redirect user to
        """
        from google_auth_oauthlib.flow import Flow
        
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
            prompt='consent'  # Force consent to get refresh token
        )
        
        return auth_url
    
    def exchange_code_for_tokens(self, auth_code: str) -> Dict[str, str]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            auth_code: Authorization code from OAuth callback
            
        Returns:
            Dictionary with access_token, refresh_token, expires_in
        """
        from google_auth_oauthlib.flow import Flow
        
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
        
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_in": credentials.expiry.isoformat() if credentials.expiry else None
        }
    
    def _build_service(self, encrypted_access_token: str, encrypted_refresh_token: str = None):
        """Build Gmail API service with credentials"""
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
        
        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        
        return build('gmail', 'v1', credentials=credentials)
    
    async def list_messages(
        self,
        encrypted_access_token: str,
        encrypted_refresh_token: str = None,
        max_results: int = 100,
        query: str = None,
        page_token: str = None
    ) -> Dict[str, Any]:
        """
        List email messages.
        
        Args:
            encrypted_access_token: Encrypted OAuth access token
            encrypted_refresh_token: Encrypted OAuth refresh token
            max_results: Maximum number of messages to return
            query: Gmail search query (e.g., "is:unread", "from:example.com")
            page_token: Token for pagination
            
        Returns:
            Dictionary with messages list and nextPageToken
        """
        try:
            service = self._build_service(encrypted_access_token, encrypted_refresh_token)
            
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query,
                pageToken=page_token
            ).execute()
            
            return {
                "messages": results.get('messages', []),
                "next_page_token": results.get('nextPageToken'),
                "result_size_estimate": results.get('resultSizeEstimate', 0)
            }
            
        except HttpError as error:
            return {"error": str(error), "messages": []}
    
    async def get_message(
        self,
        encrypted_access_token: str,
        message_id: str,
        encrypted_refresh_token: str = None,
        format: str = 'full'
    ) -> Dict[str, Any]:
        """
        Get a specific email message.
        
        Args:
            encrypted_access_token: Encrypted OAuth access token
            message_id: Gmail message ID
            encrypted_refresh_token: Encrypted refresh token
            format: Message format ('full', 'metadata', 'raw')
            
        Returns:
            Message data with headers, body, attachments
        """
        try:
            service = self._build_service(encrypted_access_token, encrypted_refresh_token)
            
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format=format
            ).execute()
            
            # Parse message
            parsed = self._parse_message(message)
            return parsed
            
        except HttpError as error:
            return {"error": str(error)}
    
    def _parse_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail API message into structured format"""
        headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
        
        # Extract body
        body = self._get_body(message.get('payload', {}))
        
        return {
            "id": message.get('id'),
            "thread_id": message.get('threadId'),
            "subject": headers.get('Subject', ''),
            "from": headers.get('From', ''),
            "to": headers.get('To', ''),
            "cc": headers.get('Cc', ''),
            "date": headers.get('Date', ''),
            "body": body,
            "snippet": message.get('snippet', ''),
            "label_ids": message.get('labelIds', []),
            "has_attachments": 'attachment' in body.lower() or len(self._get_attachments(message.get('payload', {}))) > 0,
            "attachments": self._get_attachments(message.get('payload', {})),
            "raw_message": message
        }
    
    def _get_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload"""
        if 'parts' in payload:
            parts = payload['parts']
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        # Strip HTML tags (simplified)
                        return re.sub('<[^<]+?>', '', html)
                elif 'parts' in part:
                    # Recursive for nested parts
                    return self._get_body(part)
        else:
            if 'data' in payload.get('body', {}):
                return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return ""
    
    def _get_attachments(self, payload: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract attachment metadata"""
        attachments = []
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    attachments.append({
                        "filename": part['filename'],
                        "mime_type": part['mimeType'],
                        "size": part['body'].get('size', 0),
                        "attachment_id": part['body'].get('attachmentId')
                    })
        
        return attachments
    
    async def send_message(
        self,
        encrypted_access_token: str,
        to: str,
        subject: str,
        body: str,
        cc: str = None,
        bcc: str = None,
        encrypted_refresh_token: str = None,
        in_reply_to: str = None,
        references: str = None
    ) -> Dict[str, Any]:
        """
        Send an email via Gmail.
        
        Args:
            encrypted_access_token: Encrypted OAuth access token
            to: Recipient email(s)
            subject: Email subject
            body: Email body (plain text or HTML)
            cc: CC recipients
            bcc: BCC recipients
            encrypted_refresh_token: Encrypted refresh token
            in_reply_to: Message ID for threading
            references: Message references for threading
            
        Returns:
            Sent message data
        """
        try:
            service = self._build_service(encrypted_access_token, encrypted_refresh_token)
            
            # Create message
            message = MIMEText(body)
            message['To'] = to
            message['Subject'] = subject
            if cc:
                message['Cc'] = cc
            if bcc:
                message['Bcc'] = bcc
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
            if references:
                message['References'] = references
            
            # Encode
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            result = service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return {"success": True, "message_id": result.get('id')}
            
        except HttpError as error:
            return {"success": False, "error": str(error)}
    
    async def modify_labels(
        self,
        encrypted_access_token: str,
        message_id: str,
        add_labels: List[str] = None,
        remove_labels: List[str] = None,
        encrypted_refresh_token: str = None
    ) -> Dict[str, Any]:
        """
        Add or remove labels from a message.
        
        Args:
            encrypted_access_token: Encrypted OAuth access token
            message_id: Gmail message ID
            add_labels: List of label IDs to add
            remove_labels: List of label IDs to remove
            encrypted_refresh_token: Encrypted refresh token
            
        Returns:
            Modified message data
        """
        try:
            service = self._build_service(encrypted_access_token, encrypted_refresh_token)
            
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
            
            result = service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            ).execute()
            
            return {"success": True, "message": result}
            
        except HttpError as error:
            return {"success": False, "error": str(error)}

