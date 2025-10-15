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
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

