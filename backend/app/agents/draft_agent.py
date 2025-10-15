"""
AI Draft Agent - Generates email responses in agent's voice
Refactored to use shared prompts, types, and exceptions
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from anthropic import Anthropic

from ..config import settings
from ..shared.prompts import build_draft_prompt, DRAFT_IMPROVEMENT_TEMPLATE, DRAFT_TONE_VARIANTS
from ..shared.types import DraftVariant, AgentInfo
from ..shared.exceptions import DraftGenerationException, AnthropicAPIException

logger = logging.getLogger(__name__)


class DraftAgent:
    """
    Generates personalized email drafts for real estate agents.
    Learns from agent's writing style and adapts responses.
    
    Refactored to use:
    - Centralized prompts from shared.prompts
    - Pydantic types from shared.types  
    - Custom exceptions from shared.exceptions
    """
    
    def __init__(self, claude_client: Optional[Anthropic] = None):
        """
        Initialize draft agent.
        
        Args:
            claude_client: Optional Anthropic client for dependency injection.
                          If None, creates client from settings.
        """
        self.client = claude_client or Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    async def generate_draft(
        self,
        original_email: Dict[str, Any],
        agent_info: Dict[str, Any],
        style_examples: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        num_variants: int = 1
    ) -> List[DraftVariant]:
        """
        Generate email draft(s).
        
        Args:
            original_email: Original email to reply to
            agent_info: Agent's information and preferences
            style_examples: List of agent's previous emails for style matching
            context: Additional context (CRM, market data, property info)
            num_variants: Number of draft variants to generate (1-3)
            
        Returns:
            List of DraftVariant Pydantic models with content and metadata
            
        Raises:
            DraftGenerationException: If draft generation fails
        """
        drafts: List[DraftVariant] = []
        
        for i in range(min(num_variants, 3)):
            try:
                # Determine tone for this variant
                tone = None
                if num_variants > 1:
                    tones = ["warm", "professional", "concise"]
                    tone = tones[i]
                
                # Build prompt using centralized function
                prompt = build_draft_prompt(
                    original_email=original_email,
                    agent_info=agent_info,
                    style_examples=style_examples,
                    context=context,
                    tone=tone
                )
                
                # Call Claude
                try:
                    message = self.client.messages.create(
                        model=self.model,
                        max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7 if num_variants > 1 else 0.5  # More variation for multiple drafts
                    )
                except Exception as e:
                    logger.error(f"Anthropic API error: {str(e)}")
                    raise AnthropicAPIException(
                        f"Failed to generate draft: {str(e)}",
                        error_code="CLAUDE_DRAFT_ERROR"
                    )
                
                draft_content = message.content[0].text.strip()
                
                # Calculate confidence (simplified)
                confidence = 0.85 if style_examples else 0.70
                
                # Create DraftVariant Pydantic model
                draft = DraftVariant(
                    variant_number=i + 1,
                    content=draft_content,
                    confidence_score=confidence,
                    generated_at=datetime.utcnow().isoformat(),
                    model_version=self.model,
                    word_count=len(draft_content.split()),
                    has_call_to_action=self._has_cta(draft_content)
                )
                
                drafts.append(draft)
                
                logger.info(
                    f"Generated draft variant {i+1}: {draft.word_count} words, "
                    f"CTA={draft.has_call_to_action}, confidence={draft.confidence_score}"
                )
                
            except AnthropicAPIException:
                # Re-raise API exceptions
                raise
                
            except Exception as e:
                logger.exception(f"Error generating draft variant {i+1}: {str(e)}")
                # Add error variant
                drafts.append(DraftVariant(
                    variant_number=i + 1,
                    content="",
                    confidence_score=0.0,
                    generated_at=datetime.utcnow().isoformat(),
                    error=str(e)
                ))
        
        return drafts
    
    async def improve_draft(
        self,
        original_draft: str,
        feedback: str,
        agent_info: Dict[str, Any]
    ) -> str:
        """
        Regenerate draft based on human feedback.
        
        Args:
            original_draft: The AI-generated draft
            feedback: Human feedback on what to change
            agent_info: Agent information
            
        Returns:
            Improved draft text
            
        Raises:
            DraftGenerationException: If improvement fails
        """
        try:
            prompt = DRAFT_IMPROVEMENT_TEMPLATE.format(
                agent_name=agent_info.get('full_name', 'the agent'),
                original_draft=original_draft,
                feedback=feedback
            )
            
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                    messages=[{"role": "user", "content": prompt}]
                )
            except Exception as e:
                logger.error(f"Anthropic API error during improvement: {str(e)}")
                raise AnthropicAPIException(
                    f"Failed to improve draft: {str(e)}",
                    error_code="CLAUDE_IMPROVEMENT_ERROR"
                )
            
            improved_draft = message.content[0].text.strip()
            
            logger.info(f"Improved draft based on feedback: {len(feedback)} chars of feedback")
            
            return improved_draft
            
        except AnthropicAPIException:
            raise
            
        except Exception as e:
            logger.exception(f"Error improving draft: {str(e)}")
            raise DraftGenerationException(
                f"Failed to improve draft: {str(e)}",
                error_code="DRAFT_IMPROVEMENT_FAILED"
            )
    
    def _has_cta(self, text: str) -> bool:
        """
        Check if draft has a call-to-action.
        
        Args:
            text: Draft content
            
        Returns:
            True if CTA detected
        """
        cta_phrases = [
            "call me", "let me know", "schedule", "meeting", 
            "reach out", "contact me", "get in touch", "reply",
            "book a", "set up", "arrange"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in cta_phrases)

