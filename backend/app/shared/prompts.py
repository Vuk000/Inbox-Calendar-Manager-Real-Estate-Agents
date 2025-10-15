"""
Centralized AI prompts for consistency and maintainability
"""
from typing import Dict, Any


# Triage Agent Prompts
TRIAGE_SYSTEM_PROMPT = """You are an expert real estate transaction coordinator analyzing emails for busy real estate agents. Your job is to triage incoming emails and provide structured analysis."""

TRIAGE_ANALYSIS_TEMPLATE = """Email Details:
From: {sender}
Subject: {subject}
Received: {received_at}
Body:
{body}

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


# Draft Agent Prompts
DRAFT_SYSTEM_PROMPT = """You are drafting an email response on behalf of {agent_name}, a professional real estate agent."""

DRAFT_INSTRUCTIONS = """Instructions:
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

DRAFT_TONE_VARIANTS = {
    "warm": "Write this in a warm, friendly tone.",
    "professional": "Write this in a professional, formal tone.",
    "concise": "Write this in a concise, direct tone."
}

DRAFT_IMPROVEMENT_TEMPLATE = """You previously drafted this email for {agent_name}:

{original_draft}

The agent provided this feedback:
{feedback}

Please revise the draft according to the feedback while maintaining professionalism and clarity.

Return ONLY the revised email text:"""


# Lead Qualification Agent Prompts
LEAD_QUAL_SYSTEM_PROMPT = """You are a real estate lead qualification expert. Analyze this lead inquiry email and extract key information."""

LEAD_QUAL_ANALYSIS_TEMPLATE = """Email:
From: {sender_email} ({sender_name})
Subject: {subject}
Body:
{body}

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

LEAD_QUAL_QUESTIONS_TEMPLATE = """Write a friendly email to a real estate lead asking qualifying questions.

Missing information: {missing_info}

The email should:
1. Thank them for reaching out
2. Express enthusiasm about helping them
3. Ask 3-5 specific qualifying questions naturally
4. Keep it conversational, not like a form
5. Invite them to schedule a call

Write ONLY the email body:"""


# Follow-up Agent Prompts
FOLLOW_UP_CHECK_TEMPLATE = """Analyze if this lead needs a follow-up based on:
- Last contact date: {last_contact}
- Lead score: {lead_score}
- Previous interactions: {interaction_count}
- Current status: {status}

Return JSON with:
- needs_follow_up (boolean)
- urgency (string): "high", "medium", "low"
- suggested_message (string): Brief follow-up suggestion
- best_time (string): When to follow up"""


# Negotiation Agent Prompts
NEGOTIATION_ANALYSIS_TEMPLATE = """Analyze this negotiation email:

{email_content}

Current offer: {current_offer}
Asking price: {asking_price}
Market data: {market_data}

Provide negotiation strategy in JSON:
- counter_offer_suggested (float or null)
- negotiation_points (array): Key points to emphasize
- concessions_possible (array): What can be negotiated
- red_flags (array): Concerns to address
- tone_recommendation (string): "firm", "flexible", "neutral"
- confidence (float)"""


def build_triage_prompt(email_content: Dict[str, Any]) -> str:
    """Build complete triage prompt"""
    return TRIAGE_SYSTEM_PROMPT + "\n\n" + TRIAGE_ANALYSIS_TEMPLATE.format(
        sender=email_content.get("sender_email", ""),
        subject=email_content.get("subject", ""),
        received_at=email_content.get("received_at", ""),
        body=email_content.get("body", "")[:2000]  # Limit to avoid token overflow
    )


def build_draft_prompt(
    original_email: Dict[str, Any],
    agent_info: Dict[str, Any],
    style_examples: list = None,
    context: Dict[str, Any] = None,
    tone: str = None
) -> str:
    """Build complete draft generation prompt"""
    prompt_parts = [
        DRAFT_SYSTEM_PROMPT.format(agent_name=agent_info.get("full_name", "Agent"))
    ]
    
    # Email context
    prompt_parts.append(f"""
Original Email Thread:
{original_email.get("thread_context", "")}

Latest Email from {original_email.get("sender_name", "Client")} <{original_email.get("sender_email", "")}
>:
Subject: {original_email.get("subject", "")}
{original_email.get("body", "")}
""")
    
    # Style examples
    if style_examples:
        examples_text = "\n".join(f"Example {i+1}: {ex[:300]}" for i, ex in enumerate(style_examples[:3]))
        prompt_parts.append(f"""
Writing Style Examples (from previous emails):
{examples_text}

Match this writing style: tone, formality, common phrases, email structure, and signature style.
""")
    
    # Additional context
    if context:
        context_parts = []
        if context.get("crm_data"):
            context_parts.append(f"CRM Context: {context['crm_data']}")
        if context.get("market_data"):
            context_parts.append(f"Market Data: {context['market_data']}")
        if context.get("property_data"):
            context_parts.append(f"Property Details: {context['property_data']}")
        if context_parts:
            prompt_parts.append("\n".join(context_parts))
    
    # Agent info
    prompt_parts.append(f"""
Agent Contact Info:
Name: {agent_info.get('full_name', '')}
Email: {agent_info.get('email', '')}
Phone: {agent_info.get('phone_number', '')}
""")
    
    # Instructions
    prompt_parts.append(DRAFT_INSTRUCTIONS)
    
    # Tone variation
    if tone and tone in DRAFT_TONE_VARIANTS:
        prompt_parts.append(f"\n\n{DRAFT_TONE_VARIANTS[tone]}")
    
    return "\n".join(prompt_parts)


def build_lead_qual_prompt(email_content: Dict[str, Any]) -> str:
    """Build complete lead qualification prompt"""
    return LEAD_QUAL_SYSTEM_PROMPT + "\n\n" + LEAD_QUAL_ANALYSIS_TEMPLATE.format(
        sender_email=email_content.get("sender_email", ""),
        sender_name=email_content.get("sender_name", "Unknown"),
        subject=email_content.get("subject", ""),
        body=email_content.get("body", "")
    )

