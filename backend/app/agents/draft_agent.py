"""
AI Draft Agent - Generates email responses in agent's voice
Uses Claude Sonnet 4.5 with style training
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from anthropic import Anthropic
from ..config import settings


class DraftAgent:
    """
    Generates personalized email drafts for real estate agents.
    Learns from agent's writing style and adapts responses.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    def _build_draft_prompt(
        self,
        original_email: Dict[str, Any],
        agent_info: Dict[str, Any],
        style_examples: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for draft generation"""
        
        # Extract email details
        sender = original_email.get("sender_email", "Client")
        sender_name = original_email.get("sender_name", sender)
        subject = original_email.get("subject", "")
        body = original_email.get("body", "")
        thread = original_email.get("thread_context", "")
        
        # Agent details
        agent_name = agent_info.get("full_name", "Agent")
        agent_email = agent_info.get("email", "")
        agent_phone = agent_info.get("phone_number", "")
        
        # Style analysis
        style_section = ""
        if style_examples:
            style_section = f"""
Writing Style Examples (from previous emails):
{chr(10).join(f"Example {i+1}: {ex[:300]}" for i, ex in enumerate(style_examples[:3]))}

Match this writing style: tone, formality, common phrases, email structure, and signature style.
"""
        
        # Context section
        context_section = ""
        if context:
            crm_data = context.get("crm_data", {})
            market_data = context.get("market_data", {})
            property_data = context.get("property_data", {})
            
            if crm_data:
                context_section += f"\nCRM Context: {crm_data}"
            if market_data:
                context_section += f"\nMarket Data: {market_data}"
            if property_data:
                context_section += f"\nProperty Details: {property_data}"
        
        prompt = f"""You are drafting an email response on behalf of {agent_name}, a professional real estate agent.

Original Email Thread:
{thread}

Latest Email from {sender_name} <{sender}>:
Subject: {subject}
{body}

{style_section}

{context_section}

Agent Contact Info:
Name: {agent_name}
Email: {agent_email}
Phone: {agent_phone}

Instructions:
1. Write a professional, personalized response that:
   - Addresses all questions and concerns raised
   - Maintains a warm, professional tone appropriate for real estate
   - If it's a lead inquiry: Show enthusiasm, build rapport, suggest next steps (call, showing, etc.)
   - If it's a negotiation: Be diplomatic, data-driven, professional
   - If it's a showing request: Confirm availability, provide details, set expectations
   - Uses real estate best practices and terminology
   
2. Structure:
   - Friendly greeting using their name
   - Acknowledge their message/questions
   - Provide helpful, specific information
   - Clear call-to-action or next steps
   - Professional signature

3. Keep it concise but thorough (2-4 paragraphs ideal)

4. Match the agent's writing style if examples were provided

5. Return ONLY the email body text, no subject line, no JSON, no markdown.

Draft the email now:"""

        return prompt
    
    async def generate_draft(
        self,
        original_email: Dict[str, Any],
        agent_info: Dict[str, Any],
        style_examples: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        num_variants: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Generate email draft(s).
        
        Args:
            original_email: Original email to reply to
            agent_info: Agent's information and preferences
            style_examples: List of agent's previous emails for style matching
            context: Additional context (CRM, market data, property info)
            num_variants: Number of draft variants to generate (1-3)
            
        Returns:
            List of draft dictionaries with content and metadata
        """
        drafts = []
        
        for i in range(min(num_variants, 3)):
            try:
                prompt = self._build_draft_prompt(
                    original_email, agent_info, style_examples, context
                )
                
                # Add variation instruction for multiple drafts
                if num_variants > 1:
                    variation_prompts = [
                        "Write this in a warm, friendly tone.",
                        "Write this in a professional, formal tone.",
                        "Write this in a concise, direct tone."
                    ]
                    prompt += f"\n\n{variation_prompts[i]}"
                
                # Call Claude
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7 if num_variants > 1 else 0.5  # More variation for multiple drafts
                )
                
                draft_content = message.content[0].text.strip()
                
                # Calculate confidence (simplified)
                confidence = 0.85 if style_examples else 0.70
                
                drafts.append({
                    "variant_number": i + 1,
                    "content": draft_content,
                    "confidence_score": confidence,
                    "generated_at": datetime.utcnow().isoformat(),
                    "model_version": self.model,
                    "word_count": len(draft_content.split()),
                    "has_call_to_action": any(
                        phrase in draft_content.lower() 
                        for phrase in ["call me", "let me know", "schedule", "meeting", "reach out"]
                    )
                })
                
            except Exception as e:
                drafts.append({
                    "variant_number": i + 1,
                    "content": "",
                    "confidence_score": 0.0,
                    "error": str(e),
                    "generated_at": datetime.utcnow().isoformat()
                })
        
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
        """
        prompt = f"""You previously drafted this email for {agent_info.get('full_name', 'the agent')}:

{original_draft}

The agent provided this feedback:
{feedback}

Please revise the draft according to the feedback while maintaining professionalism and clarity.

Return ONLY the revised email text:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            return f"Error regenerating draft: {str(e)}"

