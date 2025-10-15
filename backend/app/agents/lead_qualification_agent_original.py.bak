"""
Lead Qualification Agent - Scores and enriches leads from emails
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
from anthropic import Anthropic
from ..config import settings


class LeadQualificationAgent:
    """
    Analyzes lead emails and provides qualification scoring.
    Extracts key information for CRM entry.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    async def qualify_lead(self, email_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze lead email and provide qualification score.
        
        Args:
            email_content: Email data with lead inquiry
            
        Returns:
            Lead qualification data with score and extracted info
        """
        prompt = f"""You are a real estate lead qualification expert. Analyze this lead inquiry email and extract key information.

Email:
From: {email_content.get('sender_email', '')} ({email_content.get('sender_name', 'Unknown')})
Subject: {email_content.get('subject', '')}
Body:
{email_content.get('body', '')}

Provide a comprehensive lead qualification in JSON format:

1. **lead_score** (integer 0-100): Overall lead quality
   - 80-100 (Hot): Ready to act, specific needs, timeline mentioned, pre-approved
   - 50-79 (Warm): Interested, some specifics, needs nurturing
   - 0-49 (Cold): Vague interest, tire-kicker, unclear needs

2. **qualification_factors** (object):
   - budget_mentioned (boolean)
   - budget_range (string or null): e.g., "$300K-$400K"
   - timeline_mentioned (boolean)
   - timeline (string or null): e.g., "next 3 months", "immediately"
   - location_specified (boolean)
   - locations (array): Preferred areas/neighborhoods
   - buyer_or_seller (string): "buyer", "seller", "both", or "unknown"
   - property_type (string or null): "house", "condo", "land", etc.
   - bedrooms (integer or null)
   - bathrooms (float or null)
   - specific_features (array): Must-haves mentioned
   - pre_approved (boolean or null): Financing mentioned
   - working_with_agent (boolean or null): Already has representation
   - urgency_level (string): "high", "medium", "low"

3. **contact_info** (object):
   - phone_mentioned (boolean)
   - phone_number (string or null)
   - preferred_contact_method (string): "email", "phone", "text", "unknown"
   - best_time_to_contact (string or null)

4. **intent_analysis** (object):
   - primary_intent (string): "buy", "sell", "rent", "invest", "explore", "spam"
   - motivation (string): Why they're looking (upgrade, downsize, job relocation, investment, etc.)
   - pain_points (array): Concerns or challenges mentioned
   - objections (array): Potential objections detected

5. **recommended_actions** (array): Next steps to take
   - Options: "call_immediately", "send_listings", "schedule_showing", "send_market_report", 
     "ask_qualifying_questions", "nurture_campaign", "ignore"

6. **auto_response_suggested** (boolean): Should auto-send a reply?

7. **crm_tags** (array): Suggested CRM tags for this lead

8. **confidence** (float 0-1): Confidence in this analysis

Return ONLY valid JSON:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            qualification = json.loads(response_text)
            
            # Add metadata
            qualification["qualified_at"] = datetime.utcnow().isoformat()
            qualification["model_version"] = self.model
            qualification["source_email"] = email_content.get("external_id")
            
            return qualification
            
        except Exception as e:
            # Fallback
            return {
                "lead_score": 50,
                "qualification_factors": {
                    "urgency_level": "medium",
                    "buyer_or_seller": "unknown"
                },
                "recommended_actions": ["ask_qualifying_questions"],
                "auto_response_suggested": True,
                "confidence": 0.3,
                "error": str(e),
                "qualified_at": datetime.utcnow().isoformat()
            }
    
    async def generate_qualification_questions(
        self,
        lead_data: Dict[str, Any]
    ) -> str:
        """
        Generate follow-up questions to better qualify a lead.
        
        Args:
            lead_data: Initial lead qualification data
            
        Returns:
            Email text with qualifying questions
        """
        missing_info = []
        
        qual_factors = lead_data.get("qualification_factors", {})
        if not qual_factors.get("budget_mentioned"):
            missing_info.append("budget/price range")
        if not qual_factors.get("timeline_mentioned"):
            missing_info.append("timeline")
        if not qual_factors.get("location_specified"):
            missing_info.append("preferred areas")
        
        prompt = f"""Write a friendly email to a real estate lead asking qualifying questions.

Missing information: {', '.join(missing_info)}

The email should:
1. Thank them for reaching out
2. Express enthusiasm about helping them
3. Ask 3-5 specific qualifying questions naturally
4. Keep it conversational, not like a form
5. Invite them to schedule a call

Write ONLY the email body:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text.strip()
            
        except Exception:
            return "Thank you for your interest! I'd love to help you find the perfect property. Could you share a bit more about what you're looking for, including your budget range, preferred areas, and timeline? Feel free to call me directly as well!"

