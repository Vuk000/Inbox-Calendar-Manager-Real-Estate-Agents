"""
Outlook/Microsoft 365 Integration - OAuth, read, send emails
Uses Microsoft Graph API via MSAL
"""
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime, timedelta
import msal

from ..config import settings
from ..security.encryption import encrypt_data, decrypt_data


class OutlookIntegration:
    """
    Microsoft Outlook/365 integration using Graph API.
    Handles OAuth and email operations.
    """
    
    def __init__(self):
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.tenant_id = settings.MICROSOFT_TENANT_ID
        self.redirect_uri = settings.MICROSOFT_REDIRECT_URI
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = [
            "https://graph.microsoft.com/Mail.Read",
            "https://graph.microsoft.com/Mail.ReadWrite",
            "https://graph.microsoft.com/Mail.Send",
            "https://graph.microsoft.com/User.Read"
        ]
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate OAuth authorization URL.
        
        Args:
            state: Optional state for CSRF protection
            
        Returns:
            Authorization URL
        """
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        
        auth_url = app.get_authorization_request_url(
            scopes=self.scopes,
            state=state,
            redirect_uri=self.redirect_uri
        )
        
        return auth_url
    
    def exchange_code_for_tokens(self, auth_code: str) -> Dict[str, str]:
        """
        Exchange authorization code for tokens.
        
        Args:
            auth_code: Authorization code
            
        Returns:
            Dictionary with access_token, refresh_token, expires_in
        """
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        
        result = app.acquire_token_by_authorization_code(
            code=auth_code,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        if "access_token" in result:
            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token"),
                "expires_in": result.get("expires_in", 3600)
            }
        else:
            raise Exception(f"Failed to get token: {result.get('error_description')}")
    
    def _get_headers(self, encrypted_access_token: str) -> Dict[str, str]:
        """Get authorization headers"""
        access_token = decrypt_data(encrypted_access_token)
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def list_messages(
        self,
        encrypted_access_token: str,
        max_results: int = 100,
        filter_query: str = None,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        List email messages.
        
        Args:
            encrypted_access_token: Encrypted access token
            max_results: Maximum results to return
            filter_query: OData filter (e.g., "isRead eq false")
            skip: Number of messages to skip (pagination)
            
        Returns:
            Dictionary with messages and pagination
        """
        try:
            headers = self._get_headers(encrypted_access_token)
            
            params = {
                "$top": max_results,
                "$skip": skip,
                "$orderby": "receivedDateTime DESC"
            }
            
            if filter_query:
                params["$filter"] = filter_query
            
            response = requests.get(
                f"{self.graph_endpoint}/me/messages",
                headers=headers,
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "messages": data.get("value", []),
                "next_link": data.get("@odata.nextLink"),
                "count": len(data.get("value", []))
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "messages": []}
    
    async def get_message(
        self,
        encrypted_access_token: str,
        message_id: str
    ) -> Dict[str, Any]:
        """
        Get a specific message.
        
        Args:
            encrypted_access_token: Encrypted access token
            message_id: Message ID
            
        Returns:
            Message data
        """
        try:
            headers = self._get_headers(encrypted_access_token)
            
            response = requests.get(
                f"{self.graph_endpoint}/me/messages/{message_id}",
                headers=headers
            )
            
            response.raise_for_status()
            message = response.json()
            
            # Parse to standard format
            parsed = self._parse_message(message)
            return parsed
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def _parse_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Graph API message to standard format"""
        return {
            "id": message.get("id"),
            "thread_id": message.get("conversationId"),
            "subject": message.get("subject", ""),
            "from": message.get("from", {}).get("emailAddress", {}).get("address", ""),
            "from_name": message.get("from", {}).get("emailAddress", {}).get("name", ""),
            "to": [r["emailAddress"]["address"] for r in message.get("toRecipients", [])],
            "cc": [r["emailAddress"]["address"] for r in message.get("ccRecipients", [])],
            "date": message.get("receivedDateTime", ""),
            "body": message.get("body", {}).get("content", ""),
            "body_preview": message.get("bodyPreview", ""),
            "is_read": message.get("isRead", False),
            "has_attachments": message.get("hasAttachments", False),
            "importance": message.get("importance", "normal"),
            "raw_message": message
        }
    
    async def send_message(
        self,
        encrypted_access_token: str,
        to: List[str],
        subject: str,
        body: str,
        cc: List[str] = None,
        bcc: List[str] = None,
        body_type: str = "Text"
    ) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            encrypted_access_token: Encrypted access token
            to: List of recipient emails
            subject: Subject line
            body: Email body
            cc: CC recipients
            bcc: BCC recipients
            body_type: "Text" or "HTML"
            
        Returns:
            Send result
        """
        try:
            headers = self._get_headers(encrypted_access_token)
            
            message = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": body_type,
                        "content": body
                    },
                    "toRecipients": [{"emailAddress": {"address": addr}} for addr in to]
                }
            }
            
            if cc:
                message["message"]["ccRecipients"] = [{"emailAddress": {"address": addr}} for addr in cc]
            if bcc:
                message["message"]["bccRecipients"] = [{"emailAddress": {"address": addr}} for addr in bcc]
            
            response = requests.post(
                f"{self.graph_endpoint}/me/sendMail",
                headers=headers,
                json=message
            )
            
            response.raise_for_status()
            
            return {"success": True, "status_code": response.status_code}
            
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    async def mark_as_read(
        self,
        encrypted_access_token: str,
        message_id: str,
        is_read: bool = True
    ) -> Dict[str, Any]:
        """
        Mark message as read/unread.
        
        Args:
            encrypted_access_token: Encrypted access token
            message_id: Message ID
            is_read: True to mark as read, False for unread
            
        Returns:
            Update result
        """
        try:
            headers = self._get_headers(encrypted_access_token)
            
            response = requests.patch(
                f"{self.graph_endpoint}/me/messages/{message_id}",
                headers=headers,
                json={"isRead": is_read}
            )
            
            response.raise_for_status()
            
            return {"success": True}
            
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

