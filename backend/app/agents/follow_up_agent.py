"""
Follow-up sequence agent for automated lead nurturing
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from anthropic import Anthropic
from ..config import settings


class FollowUpAgent:
    """
    Manages automated follow-up sequences for leads.
    Creates nurture campaigns based on lead stage and engagement.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    async def generate_follow_up_sequence(
        self,
        lead_data: Dict[str, Any],
        agent_info: Dict[str, Any],
        num_touches: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate a multi-touch follow-up sequence.
        
        Args:
            lead_data: Lead information and context
            agent_info: Agent details
            num_touches: Number of follow-ups to generate (default 5)
            
        Returns:
            List of follow-up emails with timing
        """
        sequence = []
        
        # Define timing for each touch
        timings = [
            {"day": 1, "purpose": "Initial response"},
            {"day": 3, "purpose": "Value-add content"},
            {"day": 7, "purpose": "Objection handling"},
            {"day": 14, "purpose": "Social proof"},
            {"day": 30, "purpose": "Re-engagement"}
        ]
        
        for i, timing in enumerate(timings[:num_touches]):
            prompt = f"""Generate a follow-up email for a real estate lead nurture sequence.

Lead Information:
Name: {lead_data.get('name', 'Prospect')}
Email: {lead_data.get('email', '')}
Interest: {lead_data.get('interest', 'buying property')}
Budget: {lead_data.get('budget', 'not specified')}
Timeline: {lead_data.get('timeline', 'flexible')}
Lead Score: {lead_data.get('lead_score', 50)}/100
Original Inquiry: {lead_data.get('original_message', '')}

Agent: {agent_info.get('full_name', '')}
Phone: {agent_info.get('phone_number', '')}

Sequence Position: Email {i+1} of {num_touches} (Day {timing['day']})
Purpose: {timing['purpose']}

Instructions for this email:
{self._get_sequence_instructions(i, timing['purpose'])}

Write a warm, professional email that:
1. Is personalized to the lead's situation
2. Provides genuine value
3. Builds trust and rapport
4. Has a clear but gentle call-to-action
5. Doesn't feel salesy or pushy

Return ONLY the email body text:"""

            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                email_content = message.content[0].text.strip()
                
                sequence.append({
                    "touch_number": i + 1,
                    "send_after_days": timing["day"],
                    "purpose": timing["purpose"],
                    "subject": self._generate_subject(timing['purpose'], lead_data),
                    "body": email_content,
                    "send_time": "09:00",  # 9 AM local time
                    "skip_if_replied": True
                })
                
            except Exception as e:
                sequence.append({
                    "touch_number": i + 1,
                    "send_after_days": timing["day"],
                    "purpose": timing["purpose"],
                    "error": str(e)
                })
        
        return sequence
    
    def _get_sequence_instructions(self, touch_number: int, purpose: str) -> str:
        """Get specific instructions for each touch"""
        instructions = {
            0: """This is the initial response. Thank them for reaching out, express enthusiasm, 
                  ask 1-2 qualifying questions, and invite them to schedule a call or meeting.
                  Keep it warm and welcoming.""",
            
            1: """This is a value-add touch. Share something useful like:
                  - Market report for their area of interest
                  - Recent similar listings that match their criteria
                  - Neighborhood guide or local insights
                  Don't ask for anything, just provide value.""",
            
            2: """Address potential objections they might have:
                  - If they mentioned price concerns, discuss financing options
                  - If timing was an issue, share why now might be good
                  - Provide reassurance and expertise
                  End with "What questions can I answer for you?" """,
            
            3: """Share social proof and build credibility:
                  - Brief success story or testimonial
                  - Recent successful transaction in their area
                  - Your expertise and track record
                  Make it about helping them, not bragging.""",
            
            4: """Final re-engagement attempt. This is softer:
                  - Acknowledge they may have found something or aren't ready
                  - Offer to keep them on your list for future opportunities
                  - Leave door open: "No pressure, just wanted to check in"
                  - Provide easy way to stay connected"""
        }
        
        return instructions.get(touch_number, "Provide helpful, relevant information.")
    
    def _generate_subject(self, purpose: str, lead_data: Dict[str, Any]) -> str:
        """Generate subject line for follow-up"""
        subjects = {
            "Initial response": f"Re: Your inquiry about {lead_data.get('interest', 'properties')}",
            "Value-add content": f"Market insights for {lead_data.get('location', 'your area')}",
            "Objection handling": "Answering your questions about buying",
            "Social proof": "Recent success story you might find interesting",
            "Re-engagement": "Just checking in"
        }
        
        return subjects.get(purpose, "Following up on your property search")
    
    async def check_if_should_send(
        self,
        lead_email: str,
        last_interaction: Optional[datetime],
        touch_number: int
    ) -> Dict[str, bool]:
        """
        Check if we should send the next follow-up.
        
        Args:
            lead_email: Lead's email
            last_interaction: Last time they responded
            touch_number: Which touch in sequence
            
        Returns:
            Dictionary with send decision and reasoning
        """
        # If they replied, pause sequence
        if last_interaction and (datetime.utcnow() - last_interaction).days < 2:
            return {
                "should_send": False,
                "reason": "Lead recently engaged, pause sequence"
            }
        
        # Continue sequence
        return {
            "should_send": True,
            "reason": f"Ready for touch {touch_number}"
        }

