"""
AI Triage Agent - Analyzes and prioritizes emails for real estate agents
Refactored to use shared prompts, types, and exceptions
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re
import logging
from anthropic import Anthropic

from ..config import settings
from ..shared.prompts import build_triage_prompt
from ..shared.types import EmailContent, TriageResult, EmailEntities
from ..shared.exceptions import TriageException, AnthropicAPIException

logger = logging.getLogger(__name__)


class TriageAgent:
    """
    Intelligent email triage agent specialized for real estate.
    Classifies priority, category, extracts entities, and suggests actions.
    
    Refactored to use:
    - Centralized prompts from shared.prompts
    - Pydantic types from shared.types
    - Custom exceptions from shared.exceptions
    """
    
    def __init__(self, claude_client: Optional[Anthropic] = None):
        """
        Initialize triage agent.
        
        Args:
            claude_client: Optional Anthropic client for dependency injection.
                          If None, creates client from settings.
        """
        self.client = claude_client or Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        
    async def analyze_email(self, email_content: Dict[str, Any]) -> TriageResult:
        """
        Analyze email and return triage results.
        
        Args:
            email_content: Dictionary with email data (subject, body, sender, etc.)
            
        Returns:
            TriageResult: Pydantic model with structured triage analysis
            
        Raises:
            TriageException: If triage analysis fails
            AnthropicAPIException: If Claude API call fails
        """
        try:
            # Build prompt using centralized function
            prompt = build_triage_prompt(email_content)
            
            # Call Claude via Anthropic API
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                    messages=[{"role": "user", "content": prompt}]
                )
            except Exception as e:
                logger.error(f"Anthropic API error: {str(e)}")
                raise AnthropicAPIException(
                    f"Failed to call Claude API: {str(e)}",
                    error_code="CLAUDE_API_ERROR"
                )
            
            # Extract response text
            response_text = message.content[0].text
            
            # Parse JSON response
            try:
                analysis_dict = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error, using fallback: {str(e)}")
                return self._fallback_analysis(email_content, f"JSON decode error: {str(e)}")
            
            # Convert entities dict to EmailEntities Pydantic model
            entities_data = analysis_dict.get("entities", {})
            entities = EmailEntities(**entities_data)
            
            # Create TriageResult Pydantic model
            triage_result = TriageResult(
                priority=analysis_dict.get("priority", "low"),
                urgency_score=analysis_dict.get("urgency_score", 20.0),
                category=analysis_dict.get("category", "general"),
                entities=entities,
                suggested_actions=analysis_dict.get("suggested_actions", []),
                sentiment_score=analysis_dict.get("sentiment_score", 0.0),
                key_points=analysis_dict.get("key_points", []),
                deadline_detected=analysis_dict.get("deadline_detected"),
                requires_urgent_response=analysis_dict.get("requires_urgent_response", False),
                confidence=analysis_dict.get("confidence", 0.7),
                model_version=self.model,
                analyzed_at=datetime.utcnow().isoformat()
            )
            
            logger.info(
                f"Triaged email: priority={triage_result.priority}, "
                f"category={triage_result.category}, "
                f"urgency={triage_result.urgency_score}"
            )
            
            return triage_result
            
        except AnthropicAPIException:
            # Re-raise API exceptions
            raise
            
        except Exception as e:
            logger.exception(f"Unexpected error in triage analysis: {str(e)}")
            # Use fallback for unexpected errors
            return self._fallback_analysis(email_content, str(e))
    
    def _fallback_analysis(self, email_content: Dict[str, Any], error: str) -> TriageResult:
        """
        Fallback rule-based analysis if AI fails.
        Simple keyword-based triage.
        
        Args:
            email_content: Email data
            error: Error message that caused fallback
            
        Returns:
            TriageResult: Basic triage result with fallback indicator
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
        
        # Extract entities using utility methods
        entities = EmailEntities(
            property_addresses=self._extract_addresses(body),
            dollar_amounts=self._extract_dollars(text),
            dates=[],
            people=[],
            mls_numbers=[]
        )
        
        return TriageResult(
            priority=priority,
            urgency_score=urgency_score,
            category=category,
            entities=entities,
            suggested_actions=["reply"] if priority != "low" else [],
            sentiment_score=0.0,
            key_points=["Email analysis failed - using fallback", f"Error: {error}"],
            deadline_detected=None,
            requires_urgent_response=(priority == "high"),
            confidence=0.3,
            model_version="fallback",
            analyzed_at=datetime.utcnow().isoformat(),
            error=error
        )
    
    def _extract_addresses(self, text: str) -> List[str]:
        """
        Extract property addresses using regex.
        
        Args:
            text: Text to extract addresses from
            
        Returns:
            List of extracted addresses
        """
        # Simple pattern - in production, use NER
        pattern = r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)'
        addresses = re.findall(pattern, text, re.IGNORECASE)
        return list(set(addresses))[:5]  # Limit to 5
    
    def _extract_dollars(self, text: str) -> List[str]:
        """
        Extract dollar amounts.
        
        Args:
            text: Text to extract dollar amounts from
            
        Returns:
            List of dollar amounts as strings
        """
        pattern = r'\$\s*[\d,]+(?:\.\d{2})?'
        amounts = re.findall(pattern, text)
        return amounts[:10]  # Limit to 10

