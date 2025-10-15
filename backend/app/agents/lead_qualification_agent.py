"""
Lead Qualification Agent - Scores and enriches leads from emails
Refactored to use shared prompts, types, and exceptions
"""
from typing import Dict, Any
import json
import logging
from datetime import datetime
from anthropic import Anthropic

from ..config import settings
from ..shared.prompts import build_lead_qual_prompt, LEAD_QUAL_QUESTIONS_TEMPLATE
from ..shared.types import LeadQualification, QualificationFactors, ContactInfo, IntentAnalysis
from ..shared.exceptions import LeadQualificationException, AnthropicAPIException

logger = logging.getLogger(__name__)


class LeadQualificationAgent:
    """
    Analyzes lead emails and provides qualification scoring.
    Extracts key information for CRM entry.
    
    Refactored to use:
    - Centralized prompts from shared.prompts
    - Pydantic types from shared.types
    - Custom exceptions from shared.exceptions
    """
    
    def __init__(self, claude_client: Anthropic = None):
        """
        Initialize lead qualification agent.
        
        Args:
            claude_client: Optional Anthropic client for dependency injection.
                          If None, creates client from settings.
        """
        self.client = claude_client or Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    async def qualify_lead(self, email_content: Dict[str, Any]) -> LeadQualification:
        """
        Analyze lead email and provide qualification score.
        
        Args:
            email_content: Email data with lead inquiry
            
        Returns:
            LeadQualification: Pydantic model with structured qualification data
            
        Raises:
            LeadQualificationException: If qualification fails
            AnthropicAPIException: If Claude API call fails
        """
        try:
            # Build prompt using centralized function
            prompt = build_lead_qual_prompt(email_content)
            
            # Call Claude
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                    messages=[{"role": "user", "content": prompt}]
                )
            except Exception as e:
                logger.error(f"Anthropic API error: {str(e)}")
                raise AnthropicAPIException(
                    f"Failed to qualify lead: {str(e)}",
                    error_code="CLAUDE_LEAD_QUAL_ERROR"
                )
            
            response_text = message.content[0].text
            
            # Parse JSON response
            try:
                qualification_dict = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error in lead qualification, using fallback: {str(e)}")
                return self._fallback_qualification(email_content, str(e))
            
            # Build Pydantic models from dict
            qual_factors_dict = qualification_dict.get("qualification_factors", {})
            qual_factors = QualificationFactors(**qual_factors_dict)
            
            contact_info_dict = qualification_dict.get("contact_info")
            contact_info = ContactInfo(**contact_info_dict) if contact_info_dict else None
            
            intent_dict = qualification_dict.get("intent_analysis")
            intent_analysis = IntentAnalysis(**intent_dict) if intent_dict else None
            
            # Create LeadQualification Pydantic model
            qualification = LeadQualification(
                lead_score=qualification_dict.get("lead_score", 50),
                qualification_factors=qual_factors,
                contact_info=contact_info,
                intent_analysis=intent_analysis,
                recommended_actions=qualification_dict.get("recommended_actions", []),
                auto_response_suggested=qualification_dict.get("auto_response_suggested", False),
                crm_tags=qualification_dict.get("crm_tags", []),
                confidence=qualification_dict.get("confidence", 0.7),
                qualified_at=datetime.utcnow().isoformat(),
                model_version=self.model,
                source_email=email_content.get("external_id")
            )
            
            logger.info(
                f"Qualified lead: score={qualification.lead_score}, "
                f"intent={qualification.intent_analysis.primary_intent if qualification.intent_analysis else 'unknown'}, "
                f"urgency={qualification.qualification_factors.urgency_level}"
            )
            
            return qualification
            
        except AnthropicAPIException:
            # Re-raise API exceptions
            raise
            
        except Exception as e:
            logger.exception(f"Unexpected error in lead qualification: {str(e)}")
            return self._fallback_qualification(email_content, str(e))
    
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
            
        Raises:
            LeadQualificationException: If question generation fails
        """
        try:
            # Determine missing information
            missing_info = []
            
            qual_factors = lead_data.get("qualification_factors", {})
            if not qual_factors.get("budget_mentioned"):
                missing_info.append("budget/price range")
            if not qual_factors.get("timeline_mentioned"):
                missing_info.append("timeline")
            if not qual_factors.get("location_specified"):
                missing_info.append("preferred areas")
            
            # Build prompt
            prompt = LEAD_QUAL_QUESTIONS_TEMPLATE.format(
                missing_info=', '.join(missing_info) if missing_info else "general information"
            )
            
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
            except Exception as e:
                logger.error(f"Anthropic API error during question generation: {str(e)}")
                # Use fallback
                return self._fallback_questions()
            
            questions_text = message.content[0].text.strip()
            
            logger.info(f"Generated qualification questions for {len(missing_info)} missing fields")
            
            return questions_text
            
        except Exception as e:
            logger.exception(f"Error generating qualification questions: {str(e)}")
            return self._fallback_questions()
    
    def _fallback_qualification(self, email_content: Dict[str, Any], error: str) -> LeadQualification:
        """
        Fallback basic qualification when AI fails.
        
        Args:
            email_content: Email data
            error: Error message
            
        Returns:
            LeadQualification: Basic qualification with fallback indicator
        """
        # Basic keyword detection
        text = (email_content.get("subject", "") + " " + email_content.get("body", "")).lower()
        
        # Simple scoring
        lead_score = 50  # Default medium
        if any(word in text for word in ["urgent", "immediate", "asap", "pre-approved"]):
            lead_score = 75
        if any(word in text for word in ["just looking", "maybe", "curious"]):
            lead_score = 30
        
        # Minimal factors
        qual_factors = QualificationFactors(
            urgency_level="medium",
            buyer_or_seller="unknown"
        )
        
        # Minimal intent
        intent = IntentAnalysis(
            primary_intent="explore"
        )
        
        return LeadQualification(
            lead_score=lead_score,
            qualification_factors=qual_factors,
            intent_analysis=intent,
            recommended_actions=["ask_qualifying_questions"],
            auto_response_suggested=True,
            crm_tags=["unqualified", "needs-follow-up"],
            confidence=0.3,
            qualified_at=datetime.utcnow().isoformat(),
            model_version="fallback",
            error=error
        )
    
    def _fallback_questions(self) -> str:
        """
        Fallback qualification questions.
        
        Returns:
            Basic question template
        """
        return """Thank you for your interest! I'd love to help you find the perfect property. 

To better assist you, could you share a bit more about what you're looking for?
- What's your budget range?
- What areas are you interested in?
- What's your timeline for moving?
- Any specific features or requirements?

Feel free to call me directly as well - I'm here to help!"""

