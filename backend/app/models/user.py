"""User model with enterprise security"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from ..db import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    AGENT = "agent"
    TEAM_MEMBER = "team_member"


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enumeration"""
    FREE_TRIAL = "free_trial"
    SOLO_AGENT = "solo_agent"
    PRO_AGENT = "pro_agent"
    TEAM_BROKERAGE = "team_brokerage"
    ENTERPRISE = "enterprise"
    
    @classmethod
    def to_simple_tier(cls, tier: "SubscriptionTier") -> str:
        """
        Map subscription tier to simple tier string for API compatibility.
        
        Maps:
        - FREE_TRIAL -> 'free'
        - SOLO_AGENT -> 'solo'
        - PRO_AGENT -> 'pro'
        - TEAM_BROKERAGE -> 'team'
        - ENTERPRISE -> 'team'
        """
        mapping = {
            cls.FREE_TRIAL: "free",
            cls.SOLO_AGENT: "solo",
            cls.PRO_AGENT: "pro",
            cls.TEAM_BROKERAGE: "team",
            cls.ENTERPRISE: "team"
        }
        return mapping.get(tier, "free")
    
    @classmethod
    def from_simple_tier(cls, simple_tier: str) -> "SubscriptionTier":
        """
        Map simple tier string to SubscriptionTier enum.
        
        Maps:
        - 'free' -> FREE_TRIAL
        - 'solo' -> SOLO_AGENT
        - 'pro' -> PRO_AGENT
        - 'team' -> TEAM_BROKERAGE (default for team)
        """
        mapping = {
            "free": cls.FREE_TRIAL,
            "solo": cls.SOLO_AGENT,
            "pro": cls.PRO_AGENT,
            "team": cls.TEAM_BROKERAGE
        }
        return mapping.get(simple_tier.lower(), cls.FREE_TRIAL)


class User(Base):
    """User model with encrypted credentials and RBAC"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone_number = Column(String(50))
    
    # Role-based access control
    role = Column(SQLEnum(UserRole), default=UserRole.AGENT, nullable=False)
    
    # Subscription
    subscription_tier = Column(
        SQLEnum(SubscriptionTier), 
        default=SubscriptionTier.FREE_TRIAL, 
        nullable=False
    )
    subscription_status = Column(String(50), default="active")  # active, cancelled, expired
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    # Settings (stored as JSON)
    settings = Column(JSON, default={
        "voice_style": {},
        "custom_rules": [],
        "notification_preferences": {},
        "timezone": "America/New_York",
        "language": "en"
    })
    
    # AI Usage Tracking
    ai_actions_this_month = Column(Integer, default=0)
    ai_actions_limit = Column(Integer, default=500)  # Based on tier
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_onboarded = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    email_accounts = relationship("EmailAccount", back_populates="user", cascade="all, delete-orphan")
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    drafts = relationship("Draft", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    analytics = relationship("Analytics", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # New CRM relationships
    owned_team = relationship("Team", back_populates="owner", foreign_keys="Team.owner_id", uselist=False)
    team_memberships = relationship("TeamMember", back_populates="user", foreign_keys="TeamMember.user_id")
    contacts = relationship("Contact", back_populates="user", foreign_keys="Contact.user_id")
    transactions = relationship("Transaction", back_populates="user")
    communications = relationship("CommunicationLog", back_populates="user")
    notes = relationship("Note", back_populates="user")
    ai_actions = relationship("AIAction", back_populates="user")
    landing_pages = relationship("LandingPage", back_populates="user")
    
    # VisionHome AI & Neighborhood Whisper relationships
    vision_scans = relationship("VisionScan", back_populates="user", cascade="all, delete-orphan")
    neighborhood_reports = relationship("NeighborhoodReport", back_populates="user", cascade="all, delete-orphan")
    approval_queue_items = relationship("ApprovalQueue", foreign_keys="ApprovalQueue.user_id", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    def get_simple_tier(self) -> str:
        """Get simple tier string for this user"""
        return SubscriptionTier.to_simple_tier(self.subscription_tier)
    
    def is_premium_tier(self) -> bool:
        """Check if user has premium tier (pro or team)"""
        return self.subscription_tier in [
            SubscriptionTier.PRO_AGENT,
            SubscriptionTier.TEAM_BROKERAGE,
            SubscriptionTier.ENTERPRISE
        ]

