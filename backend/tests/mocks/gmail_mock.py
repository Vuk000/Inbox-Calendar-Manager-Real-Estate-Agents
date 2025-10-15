"""
Mock responses for Gmail API
"""
from typing import Dict, Any, List
from datetime import datetime


class MockGmailService:
    """Mock Gmail API service"""
    
    @staticmethod
    def get_mock_messages_list(count: int = 5) -> Dict[str, Any]:
        """Generate mock messages list response"""
        return {
            "messages": [
                {"id": f"msg_{i}", "threadId": f"thread_{i}"}
                for i in range(count)
            ],
            "nextPageToken": "next_page_token_123",
            "resultSizeEstimate": count
        }
    
    @staticmethod
    def get_mock_message(message_id: str = "msg_1") -> Dict[str, Any]:
        """Generate mock message detail"""
        return {
            "id": message_id,
            "threadId": "thread_1",
            "labelIds": ["INBOX", "UNREAD"],
            "snippet": "This is a test email about property...",
            "payload": {
                "headers": [
                    {"name": "From", "value": "client@example.com"},
                    {"name": "To", "value": "agent@example.com"},
                    {"name": "Subject", "value": "Interested in 123 Main St"},
                    {"name": "Date", "value": "Wed, 14 Oct 2025 10:00:00 -0700"}
                ],
                "body": {
                    "data": "SSBhbSBpbnRlcmVzdGVkIGluIHZpZXdpbmcgdGhlIHByb3BlcnR5IGF0IDEyMyBNYWluIFN0cmVldC4="  # Base64 encoded
                }
            },
            "internalDate": "1697284800000",
            "historyId": "12345"
        }
    
    @staticmethod
    def get_mock_send_response() -> Dict[str, Any]:
        """Generate mock send response"""
        return {
            "id": "msg_sent_123",
            "threadId": "thread_1",
            "labelIds": ["SENT"]
        }


class MockGmailMessages:
    """Mock Gmail messages resource"""
    
    def list(self, userId: str = "me", **kwargs):
        return MockGmailListExecutor()
    
    def get(self, userId: str = "me", id: str = None, **kwargs):
        return MockGmailGetExecutor(id)
    
    def send(self, userId: str = "me", body: Dict = None):
        return MockGmailSendExecutor()


class MockGmailListExecutor:
    def execute(self):
        return MockGmailService.get_mock_messages_list()


class MockGmailGetExecutor:
    def __init__(self, message_id: str):
        self.message_id = message_id
        
    def execute(self):
        return MockGmailService.get_mock_message(self.message_id)


class MockGmailSendExecutor:
    def execute(self):
        return MockGmailService.get_mock_send_response()


class MockGmailAPI:
    """Mock Gmail API client"""
    
    def __init__(self):
        self.users = lambda: self
        
    def messages(self):
        return MockGmailMessages()

