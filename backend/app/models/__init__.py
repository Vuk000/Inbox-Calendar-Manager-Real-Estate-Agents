"""Database models"""
from .user import User
from .email_account import EmailAccount
from .property import Property
from .task import Task
from .analytics import Analytics
from .audit_log import AuditLog
from .social_account import SocialAccount

# New CRM models (Primary)
from .team import Team, TeamMember
from .contact import Contact
from .communication_log import CommunicationLog
from .transaction import Transaction
from .note import Note
from .ai_action import AIAction
from .landing_page import LandingPage

# Legacy models - DEPRECATED - Keep for backward compatibility only
# Use CommunicationLog instead of Message for new code
# Draft functionality should be reimplemented using CommunicationLog
from .message import Message
from .draft import Draft

__all__ = [
    "User",
    "EmailAccount",
    "Property",
    "Task",
    "Analytics",
    "AuditLog",
    "SocialAccount",
    # CRM models
    "Team",
    "TeamMember",
    "Contact",
    "CommunicationLog",
    "Transaction",
    "Note",
    "AIAction",
    "LandingPage",
    # Legacy - DEPRECATED
    "Message",
    "Draft",
]

