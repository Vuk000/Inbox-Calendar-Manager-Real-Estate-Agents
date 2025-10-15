"""
Negotiation Agent - Assists with offers, counteroffers, and negotiations
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from anthropic import Anthropic
from ..config import settings


class NegotiationAgent:
    """
    Analyzes negotiation emails and provides data-driven suggestions.
    Integrates with market data for informed counteroffers.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    async def analyze_offer(
        self,
        email_content: Dict[str, Any],
        property_data: Optional[Dict[str, Any]] = None,
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze an offer or counteroffer email.
        
        Args:
            email_content: Email with offer details
            property_data: Property information (listing price, details)
            market_data: Comparable sales, market trends
            
        Returns:
            Negotiation analysis and suggestions
        """
        # Build context
        property_section = ""
        if property_data:
            property_section = f"""
Property Details:
Address: {property_data.get('address', 'N/A')}
List Price: ${property_data.get('list_price', 'N/A'):,}
Property Type: {property_data.get('property_type', 'N/A')}
Beds/Baths: {property_data.get('bedrooms', 'N/A')}/{property_data.get('bathrooms', 'N/A')}
Square Feet: {property_data.get('square_feet', 'N/A'):,}
Days on Market: {property_data.get('days_on_market', 'N/A')}
"""
        
        market_section = ""
        if market_data:
            comps = market_data.get('comparables', [])
            trend = market_data.get('trend', 'stable')
            market_section = f"""
Market Data:
Market Trend: {trend}
Average Days on Market: {market_data.get('avg_days_on_market', 'N/A')}
Comparable Sales: {len(comps)} recent comps
"""
            if comps:
                market_section += "Recent Comps:\n"
                for comp in comps[:3]:
                    market_section += f"  - {comp.get('address', 'N/A')}: ${comp.get('sale_price', 0):,} ({comp.get('beds', 'N/A')}/{comp.get('baths', 'N/A')}, {comp.get('sqft', 'N/A')} sqft)\n"
        
        prompt = f"""You are a real estate negotiation expert. Analyze this offer/counteroffer email and provide strategic advice.

Email:
From: {email_content.get('sender_email', '')}
Subject: {email_content.get('subject', '')}
Body:
{email_content.get('body', '')}

{property_section}

{market_section}

Provide negotiation analysis in JSON format:

1. **offer_details** (object):
   - offer_price (number or null)
   - earnest_money (number or null)
   - contingencies (array): List any contingencies mentioned
   - closing_date (string or null)
   - financing_type (string or null): "cash", "conventional", "FHA", "VA", etc.
   - special_requests (array): Other terms or requests

2. **analysis** (object):
   - offer_vs_list_percentage (float or null): Offer as % of list price
   - strength_of_offer (string): "strong", "fair", "weak"
   - key_concerns (array): Issues or red flags
   - favorable_terms (array): Positive aspects

3. **recommendations** (object):
   - action (string): "accept", "counter", "reject", "request_best_and_final"
   - reasoning (string): Explanation of recommendation
   - suggested_counter_price (number or null): If countering
   - counter_terms_to_negotiate (array): Which terms to push back on
   - market_justification (string): How comps/market support this

4. **draft_response_outline** (string): Key points to include in response

5. **urgency** (string): "high", "medium", "low" - how quickly to respond

6. **confidence** (float 0-1): Confidence in this analysis

Return ONLY valid JSON:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            analysis = json.loads(response_text)
            
            analysis["analyzed_at"] = datetime.utcnow().isoformat()
            analysis["model_version"] = self.model
            
            return analysis
            
        except Exception as e:
            return {
                "offer_details": {},
                "analysis": {
                    "strength_of_offer": "unknown",
                    "key_concerns": ["Unable to analyze - see original email"]
                },
                "recommendations": {
                    "action": "review_manually",
                    "reasoning": "Automated analysis failed"
                },
                "urgency": "high",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def generate_counter_offer(
        self,
        original_offer: Dict[str, Any],
        counter_terms: Dict[str, Any],
        agent_info: Dict[str, Any]
    ) -> str:
        """
        Generate a professional counteroffer email.
        
        Args:
            original_offer: Original offer analysis
            counter_terms: Desired counter terms
            agent_info: Agent information
            
        Returns:
            Counteroffer email text
        """
        prompt = f"""Write a professional counteroffer email for a real estate agent.

Original Offer Details:
{json.dumps(original_offer, indent=2)}

Counter Terms:
Price: ${counter_terms.get('counter_price', 0):,}
Closing Date: {counter_terms.get('closing_date', 'flexible')}
Other Terms: {counter_terms.get('other_terms', 'as offered')}
Reasoning: {counter_terms.get('reasoning', 'Based on market analysis')}

Agent: {agent_info.get('full_name', '')}

The email should:
1. Be diplomatic and professional
2. Acknowledge the original offer positively
3. Present the counter terms clearly
4. Provide brief justification (market comps, property value)
5. Keep the door open for further negotiation
6. Express appreciation and desire to work together

Write ONLY the email body:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text.strip()
            
        except Exception:
            return f"Thank you for your offer. After careful consideration and review of current market conditions, we would like to present a counteroffer of ${counter_terms.get('counter_price', 0):,}. We believe this reflects the true value of the property and are open to discussing the terms further. Please let me know your thoughts."

