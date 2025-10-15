"""Twitter/X integration for DM ingestion and sending"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from ..config import settings
from ..security.encryption import decrypt_data, encrypt_data

logger = logging.getLogger(__name__)


class TwitterIntegration:
    """Handle Twitter/X API interactions for Direct Messages."""

    API_BASE = "https://api.twitter.com/2"

    def __init__(self, access_token: Optional[str] = None, refresh_token: Optional[str] = None):
        self.client_id = settings.TWITTER_CLIENT_ID
        self.client_secret = settings.TWITTER_CLIENT_SECRET
        self.redirect_uri = settings.TWITTER_REDIRECT_URI
        self.access_token = access_token
        self.refresh_token = refresh_token

    # ------------------------------------------------------------------
    # OAuth 2.0 Flow
    # ------------------------------------------------------------------
    def get_authorization_url(self, state: str) -> str:
        """Create OAuth 2.0 authorization URL for user consent."""
        scopes = "tweet.read tweet.write users.read dm.read dm.write offline.access".replace(" ", "%20")
        return (
            "https://twitter.com/i/oauth2/authorize"
            f"?response_type=code&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={scopes}&state={state}&code_challenge=challenge&code_challenge_method=plain"
        )

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens."""
        data = {
            "client_id": self.client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "code_verifier": "challenge",
        }
        response = httpx.post("https://api.twitter.com/2/oauth2/token", data=data, timeout=30)
        response.raise_for_status()
        payload = response.json()
        logger.info("Twitter tokens exchanged successfully")
        return payload

    def refresh_access_token(self, encrypted_refresh_token: str) -> str:
        """Refresh expired access token."""
        refresh_token = decrypt_data(encrypted_refresh_token)
        data = {
            "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        response = httpx.post("https://api.twitter.com/2/oauth2/token", data=data, timeout=30)
        response.raise_for_status()
        payload = response.json()
        new_token = payload.get("access_token")
        logger.info("Twitter access token refreshed")
        return new_token

    # ------------------------------------------------------------------
    # API helpers
    # ------------------------------------------------------------------
    def _auth_headers(self, encrypted_token: str) -> Dict[str, str]:
        token = decrypt_data(encrypted_token)
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def get_authenticated_user(self, encrypted_token: str) -> Dict[str, Any]:
        """Fetch the authenticated user profile."""
        headers = self._auth_headers(encrypted_token)
        response = httpx.get(f"{self.API_BASE}/users/me", headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def list_direct_messages(self, encrypted_token: str, dm_conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """List DM events for the authenticated user."""
        headers = self._auth_headers(encrypted_token)
        params = {"event_types": "MessageCreate", "dm_conversation_id": dm_conversation_id} if dm_conversation_id else {}
        response = httpx.get(f"{self.API_BASE}/dm_events", headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def send_direct_message(
        self,
        encrypted_token: str,
        recipient_id: str,
        message: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send DM to a recipient."""
        headers = self._auth_headers(encrypted_token)
        payload = {
            "event": {
                "type": "MessageCreate",
                "message_create": {
                    "target": {"recipient_id": recipient_id},
                    "message_data": {"text": message},
                },
            }
        }
        if attachments:
            payload["event"]["message_create"]["message_data"]["attachment"] = attachments
        response = httpx.post(f"{self.API_BASE}/dm_events", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Webhook management
    # ------------------------------------------------------------------
    def register_webhook(self, encrypted_token: str, callback_url: str) -> Dict[str, Any]:
        """Register Account Activity API webhook (Enterprise/Essential)."""
        headers = self._auth_headers(encrypted_token)
        payload = {"url": callback_url, "env_name": settings.TWITTER_WEBHOOK_ENV}
        response = httpx.post(f"{self.API_BASE}/account_activity/all/{settings.TWITTER_WEBHOOK_ENV}/webhooks", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def subscribe_user(self, encrypted_token: str) -> Dict[str, Any]:
        """Create subscription for authenticated user DM events."""
        headers = self._auth_headers(encrypted_token)
        response = httpx.post(f"{self.API_BASE}/account_activity/all/{settings.TWITTER_WEBHOOK_ENV}/subscriptions", headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    @staticmethod
    def normalize_dm_event(event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Twitter DM payload into internal schema."""
        message = event.get("event") or event
        message_data = message.get("message_create", {})
        normalized = {
            "external_id": message.get("id"),
            "sender_id": message_data.get("sender_id"),
            "recipient_id": message_data.get("target", {}).get("recipient_id"),
            "text": message_data.get("message_data", {}).get("text", ""),
            "sent_at": message.get("created_timestamp"),
            "attachments": message_data.get("message_data", {}).get("attachment"),
        }
        return normalized

    @staticmethod
    def encrypt_tokens(tokens: Dict[str, Any]) -> Dict[str, str]:
        """Encrypt and return token payload for storage."""
        return {
            "encrypted_access_token": encrypt_data(tokens.get("access_token", "")),
            "encrypted_refresh_token": encrypt_data(tokens.get("refresh_token", "")),
            "expires_in": tokens.get("expires_in"),
        }
