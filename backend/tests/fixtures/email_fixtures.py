"""
Email test fixtures
"""
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any


@pytest.fixture
def offer_email() -> Dict[str, Any]:
    """High priority offer email"""
    return {
        "subject": "Offer on 456 Oak Avenue",
        "body": """Hello,

I would like to submit an offer of $525,000 for the property at 456 Oak Avenue.

I am pre-approved for up to $600,000 and can close in 30 days. I have $50,000 earnest money ready.

Please let me know if this works.

Best regards,
Sarah Johnson""",
        "sender_email": "sarah.johnson@example.com",
        "sender_name": "Sarah Johnson",
        "received_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def lead_email() -> Dict[str, Any]:
    """Medium priority lead inquiry"""
    return {
        "subject": "Looking for a 3-bedroom house",
        "body": """Hi,

I'm interested in buying a 3-bedroom house in the downtown area. My budget is around $300,000-$350,000.

I'd like to move within the next 2-3 months. Can you help me find something?

Thanks,
Mike""",
        "sender_email": "mike@example.com",
        "sender_name": "Mike",
        "received_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def showing_request_email() -> Dict[str, Any]:
    """Showing request email"""
    return {
        "subject": "Schedule Showing for 789 Pine Street",
        "body": """Good morning,

I would like to schedule a showing for the property at 789 Pine Street. I'm available this Saturday afternoon or Sunday morning.

Looking forward to seeing it!

Best,
Jennifer Martinez""",
        "sender_email": "jennifer.m@example.com",
        "sender_name": "Jennifer Martinez",
        "received_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def newsletter_email() -> Dict[str, Any]:
    """Low priority newsletter"""
    return {
        "subject": "Monthly Real Estate Market Update",
        "body": """Dear Agent,

Here's your monthly market update with trends, statistics, and insights...

[Newsletter content]

Unsubscribe | View in browser""",
        "sender_email": "newsletter@realestatenews.com",
        "sender_name": "Real Estate News",
        "received_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
    }


@pytest.fixture
def inspection_report_email() -> Dict[str, Any]:
    """High priority inspection report"""
    return {
        "subject": "URGENT: Inspection Report - 123 Main Street",
        "body": """Agent,

Please find attached the inspection report for 123 Main Street. There are several issues that need immediate attention:

1. Roof damage - $5,000 estimated repair
2. Plumbing issues in basement
3. HVAC system needs replacement

We need to discuss these findings with the buyer by end of day.

Inspector: John Smith
Date: """ + datetime.utcnow().strftime("%Y-%m-%d"),
        "sender_email": "inspector@homeinspections.com",
        "sender_name": "John Smith",
        "received_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def counteroffer_email() -> Dict[str, Any]:
    """Counteroffer negotiation email"""
    return {
        "subject": "Re: Offer - Counteroffer for 456 Oak Avenue",
        "body": """Dear Agent,

Thank you for the offer. The seller appreciates the interest but would like to counter at $550,000.

The seller is also requesting:
- 45-day close instead of 30
- Inclusion of appliances
- $10,000 additional earnest money

Please discuss with your client and respond by Friday.

Best regards,
Listing Agent""",
        "sender_email": "listing@realestate.com",
        "sender_name": "Listing Agent",
        "received_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def spam_email() -> Dict[str, Any]:
    """Spam email"""
    return {
        "subject": "🎉 WIN $1,000,000 NOW!!! Click Here!!!",
        "body": """CONGRATULATIONS!!!

You have been selected to receive $1,000,000. Click here now to claim your prize!

[Suspicious link]

Act now before it's too late!!!""",
        "sender_email": "noreply@suspicious.com",
        "sender_name": "Prize Winner",
        "received_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def multilingual_email_spanish() -> Dict[str, Any]:
    """Spanish language email"""
    return {
        "subject": "Oferta para 789 Pine Street",
        "body": """Hola,

Me gustaría presentar una oferta de $400,000 por la propiedad en 789 Pine Street.

Estoy pre-aprobado y puedo cerrar en 30 días.

Saludos,
Carlos""",
        "sender_email": "carlos@example.com",
        "sender_name": "Carlos",
        "received_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def closing_documents_email() -> Dict[str, Any]:
    """Closing documents email"""
    return {
        "subject": "Closing Documents Ready - 123 Main Street",
        "body": """Good afternoon,

The closing documents for 123 Main Street are ready for review and signature.

Closing Date: """ + (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d") + """
Time: 2:00 PM
Location: Title Company Office

Please review all documents before the closing date.

Title Officer: Jane Doe
Phone: (555) 123-4567""",
        "sender_email": "jane.doe@titlecompany.com",
        "sender_name": "Jane Doe",
        "received_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def all_email_fixtures(
    offer_email,
    lead_email,
    showing_request_email,
    newsletter_email,
    inspection_report_email,
    counteroffer_email,
    spam_email,
    closing_documents_email
):
    """Collection of all email fixtures"""
    return {
        "offer": offer_email,
        "lead": lead_email,
        "showing": showing_request_email,
        "newsletter": newsletter_email,
        "inspection": inspection_report_email,
        "counteroffer": counteroffer_email,
        "spam": spam_email,
        "closing": closing_documents_email
    }

