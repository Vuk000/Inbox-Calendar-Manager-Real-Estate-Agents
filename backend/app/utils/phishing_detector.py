"""
Anti-phishing detection using AI and pattern matching
"""
from typing import Dict, Any, List
from anthropic import Anthropic
import re
from ..config import settings


class PhishingDetector:
    """
    Detect phishing attempts and suspicious emails.
    Uses AI + rule-based detection for security.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        
        # Known phishing patterns
        self.suspicious_keywords = [
            "wire transfer", "urgent payment", "verify account",
            "suspended account", "click here immediately",
            "confirm your password", "unusual activity",
            "claim your prize", "act now", "limited time",
            "your account will be closed"
        ]
        
        self.suspicious_domains = [
            "suspicious-domain.com",  # Would populate with known phishing domains
        ]
    
    async def analyze_email(
        self,
        email_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze email for phishing indicators.
        
        Args:
            email_data: Email content and metadata
            
        Returns:
            Analysis with risk level and flags
        """
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")
        sender = email_data.get("sender_email", "")
        
        # Rule-based checks
        rule_based_score = self._rule_based_check(subject, body, sender)
        
        # AI-powered analysis
        ai_analysis = await self._ai_phishing_check(subject, body, sender)
        
        # Combine scores
        combined_risk = max(rule_based_score, ai_analysis.get("risk_score", 0))
        
        return {
            "is_suspicious": combined_risk > 60,
            "risk_score": combined_risk,  # 0-100
            "risk_level": self._get_risk_level(combined_risk),
            "flags": ai_analysis.get("flags", []),
            "recommendations": self._get_recommendations(combined_risk),
            "rule_based_score": rule_based_score,
            "ai_score": ai_analysis.get("risk_score", 0)
        }
    
    def _rule_based_check(self, subject: str, body: str, sender: str) -> int:
        """Simple rule-based phishing detection"""
        score = 0
        text = f"{subject} {body}".lower()
        
        # Check for suspicious keywords
        keyword_matches = sum(1 for kw in self.suspicious_keywords if kw in text)
        score += keyword_matches * 15
        
        # Check sender domain
        if any(domain in sender for domain in self.suspicious_domains):
            score += 50
        
        # Check for excessive urgency
        if text.count("urgent") > 2 or text.count("immediately") > 1:
            score += 20
        
        # Check for multiple exclamation marks
        if text.count("!") > 5:
            score += 15
        
        # Check for suspicious links
        if "http://" in body:  # Non-HTTPS links
            score += 10
        
        return min(score, 100)
    
    async def _ai_phishing_check(
        self,
        subject: str,
        body: str,
        sender: str
    ) -> Dict[str, Any]:
        """AI-powered phishing detection"""
        prompt = f"""You are a cybersecurity expert specializing in email phishing detection for real estate agents.

Analyze this email for phishing indicators:

From: {sender}
Subject: {subject}
Body:
{body[:1000]}

Provide analysis in JSON format:

1. **risk_score** (integer 0-100): Overall phishing risk
   - 0-30: Likely legitimate
   - 31-60: Suspicious, review carefully
   - 61-100: High risk, likely phishing

2. **flags** (array): Specific concerns detected:
   - Options: "urgent_language", "suspicious_link", "requests_payment", 
     "requests_credentials", "spoofed_sender", "unusual_request",
     "poor_grammar", "generic_greeting", "threatens_action"

3. **legitimate_indicators** (array): Signs email might be real

4. **recommendation** (string): "safe", "caution", "block"

5. **explanation** (string): Brief explanation of the risk assessment

Return ONLY valid JSON:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            response_text = message.content[0].text
            analysis = json.loads(response_text)
            
            return analysis
            
        except Exception as e:
            return {
                "risk_score": 30,  # Default to medium-low
                "flags": [],
                "recommendation": "caution",
                "error": str(e)
            }
    
    def _get_risk_level(self, score: int) -> str:
        """Convert score to risk level"""
        if score >= 70:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"
    
    def _get_recommendations(self, score: int) -> List[str]:
        """Get security recommendations based on score"""
        if score >= 70:
            return [
                "Do not click any links in this email",
                "Do not provide any personal or financial information",
                "Verify sender through alternative communication method",
                "Report this email as phishing",
                "Delete immediately"
            ]
        elif score >= 40:
            return [
                "Verify sender identity before responding",
                "Hover over links to check destination",
                "Be cautious with attachments",
                "Contact sender via known phone number to verify"
            ]
        else:
            return [
                "Email appears legitimate",
                "Still verify any unusual requests",
                "Use caution with financial information"
            ]

