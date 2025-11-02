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

# VisionHome AI & Neighborhood Whisper models
from .vision_scan import VisionScan
from .neighborhood_report import NeighborhoodReport
from .approval_queue import ApprovalQueue, ApprovalFeatureType, ApprovalStatus

# Legacy models - DEPRECATED
# Message model has been removed - use CommunicationLog instead
# Draft functionality should be reimplemented using CommunicationLog
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
    # VisionHome AI & Neighborhood Whisper
    "VisionScan",
    "NeighborhoodReport",
    "ApprovalQueue",
    "ApprovalFeatureType",
    "ApprovalStatus",
    # Legacy - DEPRECATED
    "Draft",
]

