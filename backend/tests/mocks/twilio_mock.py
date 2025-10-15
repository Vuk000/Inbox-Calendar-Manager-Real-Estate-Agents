"""
Mock responses for Twilio API
"""
from typing import Dict, Any
from datetime import datetime


class MockTwilioMessage:
    """Mock Twilio message object"""
    
    def __init__(self, to: str, from_: str, body: str):
        self.sid = "SM" + "a" * 32
        self.to = to
        self.from_ = from_
        self.body = body
        self.status = "queued"
        self.date_created = datetime.utcnow()
        self.date_sent = None
        self.error_code = None
        self.error_message = None
        

class MockTwilioMessages:
    """Mock Twilio messages resource"""
    
    def create(self, to: str, from_: str, body: str) -> MockTwilioMessage:
        """Create mock message"""
        return MockTwilioMessage(to=to, from_=from_, body=body)
    
    def list(self, to: str = None, from_: str = None, limit: int = 20):
        """List mock messages"""
        return [
            MockTwilioMessage(
                to="+15551234567",
                from_="+15559876543",
                body=f"Test message {i}"
            )
            for i in range(min(limit, 5))
        ]


class MockTwilioClient:
    """Mock Twilio client"""
    
    def __init__(self, account_sid: str = None, auth_token: str = None):
        self.account_sid = account_sid or "AC" + "a" * 32
        self.auth_token = auth_token or "test_token"
        self.messages = MockTwilioMessages()

