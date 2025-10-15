"""Facebook Messenger integration for Page conversations"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from ..config import settings
from ..security.encryption import encrypt_data, decrypt_data

logger = logging.getLogger(__name__)


class FacebookMessengerIntegration:
    """Manage Meta Graph API calls for Messenger inbox."""

    GRAPH_BASE = "https://graph.facebook.com/v19.0"

    def __init__(self, page_id: Optional[str] = None, page_access_token: Optional[str] = None):
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
        self.redirect_uri = settings.FACEBOOK_REDIRECT_URI
        self.page_id = page_id or settings.FACEBOOK_PAGE_ID
        self.page_access_token = page_access_token

    # ------------------------------------------------------------------
    # OAuth & Tokens
    # ------------------------------------------------------------------
    def get_authorization_url(self, state: str) -> str:
        perms = "pages_messaging pages_manage_metadata pages_read_engagement".replace(" ", "%2C")
        return (
            "https://www.facebook.com/v19.0/dialog/oauth"
            f"?client_id={self.app_id}&redirect_uri={self.redirect_uri}"
            f"&state={state}&scope={perms}"
        )

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "client_secret": self.app_secret,
            "code": code,
        }
        response = httpx.get(f"{self.GRAPH_BASE}/oauth/access_token", params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        logger.info("Facebook user tokens exchanged")
        return payload

    def get_page_access_token(self, user_access_token: str) -> Dict[str, Any]:
        params = {"access_token": user_access_token}
        response = httpx.get(f"{self.GRAPH_BASE}/me/accounts", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        for page in data.get("data", []):
            if page.get("id") == self.page_id:
                logger.info("Page access token acquired")
                return page
        raise ValueError("Configured page not found in user accounts")

    @staticmethod
    def encrypt_tokens(page_token: str) -> Dict[str, str]:
        return {"encrypted_page_token": encrypt_data(page_token)}

    # ------------------------------------------------------------------
    # API Helpers
    # ------------------------------------------------------------------
    def _auth_params(self, encrypted_page_token: str) -> Dict[str, str]:
        return {"access_token": decrypt_data(encrypted_page_token)}

    def send_message(self, encrypted_page_token: str, recipient_psid: str, text: str) -> Dict[str, Any]:
        params = self._auth_params(encrypted_page_token)
        payload = {
            "messaging_type": "RESPONSE",
            "recipient": {"id": recipient_psid},
            "message": {"text": text},
        }
        response = httpx.post(f"{self.GRAPH_BASE}/me/messages", params=params, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_conversations(self, encrypted_page_token: str) -> Dict[str, Any]:
        params = self._auth_params(encrypted_page_token)
        params.update({"fields": "messages{message,from,to,created_time,id}"})
        response = httpx.get(f"{self.GRAPH_BASE}/{self.page_id}/conversations", params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Webhook helpers
    # ------------------------------------------------------------------
    @staticmethod
    def verify_webhook(mode: str, token: str, challenge: str) -> str:
        if mode == "subscribe" and token == settings.FACEBOOK_VERIFY_TOKEN:
            logger.info("Facebook webhook verified")
            return challenge
        raise PermissionError("Invalid webhook verification")

    @staticmethod
    def normalize_message(entry: Dict[str, Any]) -> Dict[str, Any]:
        messaging = entry.get("messaging", [{}])[0]
        message = messaging.get("message", {})
        normalized = {
            "sender_id": messaging.get("sender", {}).get("id"),
            "recipient_id": messaging.get("recipient", {}).get("id"),
            "text": message.get("text", ""),
            "mid": message.get("mid"),
            "timestamp": messaging.get("timestamp"),
            "attachments": message.get("attachments", []),
        }
        return normalized
