"""
Mock responses for Anthropic Claude API
"""
from typing import Dict, Any, List
import json


class MockClaudeMessage:
    """Mock Claude API message response"""
    def __init__(self, content: str):
        self.content = [MockClaudeContent(content)]
        

class MockClaudeContent:
    """Mock Claude API content object"""
    def __init__(self, text: str):
        self.text = text


class MockClaudeAPI:
    """Mock Anthropic Claude API client"""
    
    @staticmethod
    def get_triage_response(priority: str = "high") -> Dict[str, Any]:
        """Generate mock triage response"""
        return {
            "priority": priority,
            "urgency_score": 85.0 if priority == "high" else 50.0,
            "category": "offer",
            "entities": {
                "property_addresses": ["456 Oak Avenue"],
                "dollar_amounts": ["$525,000", "$600,000", "$50,000"],
                "dates": ["2025-10-14"],
                "people": ["Sarah Johnson"],
                "mls_numbers": []
            },
            "suggested_actions": ["reply", "contact_crm"],
            "sentiment_score": 0.75,
            "key_points": [
                "Buyer submitting offer of $525,000",
                "Pre-approved for $600,000",
                "Can close in 30 days",
                "Earnest money ready"
            ],
            "deadline_detected": "2025-11-14T00:00:00Z",
            "requires_urgent_response": True,
            "confidence": 0.92
        }
    
    @staticmethod
    def get_draft_response(tone: str = "professional") -> Dict[str, Any]:
        """Generate mock draft response"""
        return {
            "subject": "Re: Offer on 456 Oak Avenue",
            "body": """Hi Sarah,

Thank you for your offer of $525,000 on 456 Oak Avenue. I've received your submission and will review it with the seller immediately.

Your pre-approval and earnest money commitment are excellent. I'll get back to you within 24 hours with the seller's response.

Best regards,
Agent""",
            "tone": tone,
            "confidence": 0.88,
            "suggestions": [
                "Consider mentioning property highlights",
                "Add call to action for next steps"
            ]
        }
    
    @staticmethod
    def get_lead_qualification_response() -> Dict[str, Any]:
        """Generate mock lead qualification response"""
        return {
            "lead_score": 85,
            "intent_level": "high",
            "budget_estimated": "$300,000-$350,000",
            "timeline": "2-3 months",
            "property_preferences": {
                "bedrooms": 3,
                "location": "downtown",
                "property_type": "house"
            },
            "next_actions": ["schedule_call", "send_listings"],
            "qualification_notes": "Serious buyer with clear budget and timeline",
            "confidence": 0.87
        }
    
    @staticmethod
    def create_mock_message(response_dict: Dict[str, Any]) -> MockClaudeMessage:
        """Create mock Claude message object"""
        return MockClaudeMessage(json.dumps(response_dict))

