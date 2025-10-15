"""
AI Triage Agent - Analyzes and prioritizes emails for real estate agents
Uses Claude Sonnet 4.5 via Anthropic API with LangChain
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re
from anthropic import Anthropic
from ..config import settings


class TriageAgent:
    """
    Intelligent email triage agent specialized for real estate.
    Classifies priority, category, extracts entities, and suggests actions.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        
    def _build_prompt(self, email_content: Dict[str, Any]) -> str:
        """Build the triage prompt for Claude"""
        subject = email_content.get("subject", "")
        body = email_content.get("body", "")
        sender = email_content.get("sender_email", "")
        received_at = email_content.get("received_at", datetime.utcnow().isoformat())
        
        prompt = f"""You are an expert real estate transaction coordinator analyzing emails for busy real estate agents. Your job is to triage incoming emails and provide structured analysis.

Email Details:
From: {sender}
Subject: {subject}
Received: {received_at}
Body:
{body[:2000]}  # Limit to avoid token overflow

Analyze this email and provide a comprehensive triage report in JSON format with the following fields:

1. **priority** (string): Classify as "high", "medium", or "low"
   - HIGH: Offers, counteroffers, inspection reports, urgent deadlines, closing documents, time-sensitive showing requests
   - MEDIUM: New leads, client inquiries, property questions, general scheduling
   - LOW: Newsletters, marketing emails, non-urgent updates, spam

2. **urgency_score** (float): 0-100 numerical urgency score

3. **category** (string): One of: "offer", "counteroffer", "lead", "inspection", "closing", "showing_request", "negotiation", "general", "newsletter", "spam"

4. **entities** (object): Extract key information:
   - property_addresses: Array of property addresses mentioned
   - dollar_amounts: Array of dollar amounts found
   - dates: Array of dates mentioned (ISO format if possible)
   - people: Array of people's names mentioned
   - mls_numbers: Array of MLS/listing numbers

5. **suggested_actions** (array): List of recommended actions from:
   - "reply" - needs response
   - "schedule" - schedule showing/meeting
   - "flag_deadline" - important deadline
   - "contact_crm" - update CRM
   - "forward" - forward to team/client
   - "archive" - no action needed

6. **sentiment_score** (float): -1.0 (very negative) to 1.0 (very positive)

7. **key_points** (array): 3-5 bullet points summarizing the email

8. **deadline_detected** (string or null): If a deadline is mentioned, extract it in ISO format

9. **requires_urgent_response** (boolean): Does this need immediate attention?

10. **confidence** (float): Your confidence in this analysis (0-1)

Return ONLY valid JSON, no markdown or explanation."""

        return prompt
    
    async def analyze_email(self, email_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze email and return triage results.
        
        Args:
            email_content: Dictionary with email data (subject, body, sender, etc.)
            
        Returns:
            Dictionary with triage analysis results
        """
        try:
            prompt = self._build_prompt(email_content)
            
            # Call Claude via Anthropic API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract response text
            response_text = message.content[0].text
            
            # Parse JSON response
            analysis = json.loads(response_text)
            
            # Add metadata
            analysis["model_version"] = self.model
            analysis["analyzed_at"] = datetime.utcnow().isoformat()
            
            return analysis
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return self._fallback_analysis(email_content, str(e))
        except Exception as e:
            # Error handling
            return self._fallback_analysis(email_content, str(e))
    
    def _fallback_analysis(self, email_content: Dict[str, Any], error: str) -> Dict[str, Any]:
        """
        Fallback rule-based analysis if AI fails.
        Simple keyword-based triage.
        """
        subject = email_content.get("subject", "").lower()
        body = email_content.get("body", "").lower()
        text = f"{subject} {body}"
        
        # Priority determination
        high_keywords = ["offer", "counteroffer", "inspection", "urgent", "deadline", "closing", "expires"]
        medium_keywords = ["lead", "inquiry", "showing", "interested", "schedule", "appointment"]
        
        priority = "low"
        urgency_score = 20.0
        
        if any(kw in text for kw in high_keywords):
            priority = "high"
            urgency_score = 90.0
        elif any(kw in text for kw in medium_keywords):
            priority = "medium"
            urgency_score = 60.0
        
        # Category
        category = "general"
        if "offer" in text:
            category = "offer"
        elif "lead" in text or "interested" in text:
            category = "lead"
        elif "inspection" in text:
            category = "inspection"
        elif "showing" in text:
            category = "showing_request"
        
        return {
            "priority": priority,
            "urgency_score": urgency_score,
            "category": category,
            "entities": {
                "property_addresses": self._extract_addresses(body),
                "dollar_amounts": self._extract_dollars(text),
                "dates": [],
                "people": [],
                "mls_numbers": []
            },
            "suggested_actions": ["reply"] if priority != "low" else [],
            "sentiment_score": 0.0,
            "key_points": ["Email analysis failed - using fallback"],
            "deadline_detected": None,
            "requires_urgent_response": priority == "high",
            "confidence": 0.3,
            "model_version": "fallback",
            "analyzed_at": datetime.utcnow().isoformat(),
            "error": error
        }
    
    def _extract_addresses(self, text: str) -> List[str]:
        """Extract property addresses using regex"""
        # Simple pattern - in production, use NER
        pattern = r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)'
        addresses = re.findall(pattern, text, re.IGNORECASE)
        return list(set(addresses))[:5]  # Limit to 5
    
    def _extract_dollars(self, text: str) -> List[str]:
        """Extract dollar amounts"""
        pattern = r'\$\s*[\d,]+(?:\.\d{2})?'
        amounts = re.findall(pattern, text)
        return amounts[:10]  # Limit to 10

