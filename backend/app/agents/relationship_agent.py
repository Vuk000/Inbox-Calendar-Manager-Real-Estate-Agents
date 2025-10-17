"""
AI Relationship Scoring Agent - Analyzes contact communication history
and generates relationship strength scores
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from anthropic import Anthropic
import json
import logging

from ..config import settings
from ..shared.exceptions import AnthropicAPIException

logger = logging.getLogger(__name__)


class RelationshipAgent:
    """
    AI agent for scoring relationship strength with contacts based on
    communication patterns, frequency, sentiment, and transaction history
    """
    
    def __init__(self, claude_client: Optional[Anthropic] = None):
        """Initialize relationship agent"""
        self.client = claude_client or Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    async def calculate_relationship_score(
        self,
        contact: Dict[str, Any],
        communications: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]] = []
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive relationship score for a contact
        
        Args:
            contact: Contact data dictionary
            communications: List of communication log entries
            transactions: List of transactions with this contact
            
        Returns:
            Dict with score, insights, and recommendations
        """
        try:
            # Quick scoring based on data (fallback if AI fails)
            base_score = self._calculate_base_score(contact, communications, transactions)
            
            # Get AI-enhanced insights
            ai_insights = await self._get_ai_insights(contact, communications, transactions, base_score)
            
            return {
                "relationship_score": ai_insights.get("refined_score", base_score),
                "base_score": base_score,
                "insights": ai_insights.get("insights", []),
                "communication_pattern": ai_insights.get("communication_pattern", "Unknown"),
                "sentiment_trend": ai_insights.get("sentiment_trend", "Neutral"),
                "suggested_actions": ai_insights.get("suggested_actions", []),
                "last_contact_summary": ai_insights.get("last_contact_summary", "No recent contact")
            }
            
        except Exception as e:
            logger.error(f"Relationship scoring error: {str(e)}")
            # Return base score if AI fails
            return {
                "relationship_score": self._calculate_base_score(contact, communications, transactions),
                "base_score": base_score,
                "insights": ["Automated scoring only - AI analysis unavailable"],
                "communication_pattern": "Unknown",
                "sentiment_trend": "Neutral",
                "suggested_actions": [],
                "last_contact_summary": "No recent contact"
            }
    
    def _calculate_base_score(
        self,
        contact: Dict[str, Any],
        communications: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]]
    ) -> float:
        """Calculate base relationship score using rules"""
        score = 50.0  # Start at neutral
        
        # Factor 1: Communication frequency (0-30 points)
        comm_count = len(communications)
        if comm_count > 50:
            score += 30
        elif comm_count > 20:
            score += 20
        elif comm_count > 10:
            score += 10
        elif comm_count > 5:
            score += 5
        
        # Factor 2: Recency of last contact (0-25 points)
        if communications:
            last_comm = communications[0]  # Assuming sorted by date desc
            days_since = (datetime.utcnow() - last_comm.get("occurred_at", datetime.utcnow())).days
            
            if days_since < 7:
                score += 25
            elif days_since < 30:
                score += 20
            elif days_since < 90:
                score += 10
            elif days_since < 180:
                score += 5
        
        # Factor 3: Transaction history (0-25 points)
        if transactions:
            closed_won = sum(1 for t in transactions if t.get("stage") == "closed_won")
            active = sum(1 for t in transactions if t.get("stage") in ["active", "pending", "under_contract"])
            
            score += min(closed_won * 10, 15)  # Up to 15 points for closed deals
            score += min(active * 5, 10)  # Up to 10 points for active deals
        
        # Factor 4: Sentiment average (0-20 points)
        sentiments = [c.get("sentiment_score", 0) for c in communications if c.get("sentiment_score")]
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            # Convert -1 to 1 scale to 0 to 20 points
            score += (avg_sentiment + 1) * 10
        
        return min(max(score, 0), 100)  # Clamp between 0-100
    
    async def _get_ai_insights(
        self,
        contact: Dict[str, Any],
        communications: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]],
        base_score: float
    ) -> Dict[str, Any]:
        """Get AI-enhanced insights about the relationship"""
        
        # Prepare communication summary for AI
        recent_comms = communications[:10]  # Last 10 communications
        comm_summary = []
        
        for comm in recent_comms:
            comm_summary.append({
                "date": comm.get("occurred_at", "").isoformat() if isinstance(comm.get("occurred_at"), datetime) else str(comm.get("occurred_at")),
                "type": comm.get("communication_type"),
                "direction": comm.get("direction"),
                "summary": comm.get("summary", comm.get("subject", ""))[:200]
            })
        
        # Build prompt
        prompt = self._build_relationship_prompt(
            contact=contact,
            comm_summary=comm_summary,
            transactions=transactions,
            base_score=base_score
        )
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                system="You are an expert CRM analyst specializing in real estate relationships. Analyze communication patterns and provide actionable insights.",
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse AI response
            content = response.content[0].text
            return self._parse_ai_response(content, base_score)
            
        except Exception as e:
            logger.error(f"AI insights error: {str(e)}")
            raise AnthropicAPIException(f"Failed to get AI insights: {str(e)}")
    
    def _build_relationship_prompt(
        self,
        contact: Dict[str, Any],
        comm_summary: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]],
        base_score: float
    ) -> str:
        """Build prompt for relationship analysis"""
        return f"""Analyze this real estate contact relationship and provide insights.

CONTACT:
- Name: {contact.get('first_name')} {contact.get('last_name', '')}
- Type: {contact.get('contact_type', 'unknown')}
- Email: {contact.get('email', 'N/A')}
- Phone: {contact.get('phone', 'N/A')}

BASE RELATIONSHIP SCORE: {base_score}/100

RECENT COMMUNICATIONS ({len(comm_summary)}):
{json.dumps(comm_summary, indent=2)}

TRANSACTIONS ({len(transactions)}):
{json.dumps([{
    "stage": t.get("stage"),
    "type": t.get("transaction_type"),
    "value": t.get("estimated_value")
} for t in transactions], indent=2)}

Provide analysis in this JSON format:
{{
    "refined_score": <0-100, adjust base score if needed>,
    "insights": [
        "<insight 1>",
        "<insight 2>",
        "<insight 3>"
    ],
    "communication_pattern": "<e.g., 'Regular weekly contact', 'Infrequent check-ins', 'Highly engaged'>",
    "sentiment_trend": "<Positive/Neutral/Negative>",
    "suggested_actions": [
        "<actionable suggestion 1>",
        "<actionable suggestion 2>"
    ],
    "last_contact_summary": "<summary of most recent interaction>"
}}

Focus on:
1. Communication frequency and consistency
2. Response patterns and engagement level
3. Sentiment and relationship quality
4. Transaction conversion potential
5. Risk of losing the relationship
"""
    
    def _parse_ai_response(self, content: str, base_score: float) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        try:
            # Try to extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Validate refined score
                if "refined_score" in result:
                    result["refined_score"] = max(0, min(100, float(result["refined_score"])))
                else:
                    result["refined_score"] = base_score
                
                return result
            else:
                # Fallback if JSON not found
                return {
                    "refined_score": base_score,
                    "insights": [content[:500]],
                    "communication_pattern": "Unknown",
                    "sentiment_trend": "Neutral",
                    "suggested_actions": [],
                    "last_contact_summary": "Analysis incomplete"
                }
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI response as JSON")
            return {
                "refined_score": base_score,
                "insights": ["AI analysis failed to parse"],
                "communication_pattern": "Unknown",
                "sentiment_trend": "Neutral",
                "suggested_actions": [],
                "last_contact_summary": "Analysis incomplete"
            }
    
    def get_relationship_status(self, score: float) -> str:
        """Get human-readable relationship status from score"""
        if score >= 85:
            return "Excellent - Strong relationship"
        elif score >= 70:
            return "Good - Engaged contact"
        elif score >= 50:
            return "Fair - Moderate engagement"
        elif score >= 30:
            return "At Risk - Low engagement"
        else:
            return "Cold - Needs attention"

