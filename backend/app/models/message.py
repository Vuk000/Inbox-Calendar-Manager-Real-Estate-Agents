"""Message model for emails and multi-channel communications

DEPRECATED: This model is kept for backward compatibility only.
New code should use CommunicationLog model for logging all communications.
The Message model will be phased out in a future release.
"""
import warnings
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db import Base

# Issue deprecation warning
warnings.warn(
    "Message model is deprecated. Use CommunicationLog instead.",
    DeprecationWarning,
    stacklevel=2
)


class MessageSource(str, enum.Enum):
    """Message source channel"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TWITTER_DM = "twitter_dm"
    FACEBOOK_MESSENGER = "facebook_messenger"


class MessagePriority(str, enum.Enum):
    """AI-determined message priority"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MessageCategory(str, enum.Enum):
    """Real estate-specific message categories"""
    OFFER = "offer"
    COUNTEROFFER = "counteroffer"
    LEAD = "lead"
    INSPECTION = "inspection"
    CLOSING = "closing"
    SHOWING_REQUEST = "showing_request"
    NEGOTIATION = "negotiation"
    GENERAL = "general"
    NEWSLETTER = "newsletter"
    SPAM = "spam"


class Message(Base):
    """Unified message model with encryption and AI metadata"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    email_account_id = Column(Integer, ForeignKey("email_accounts.id"), nullable=True, index=True)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=True, index=True)
    
    # Message identification
    external_id = Column(String(255), nullable=False, index=True)  # Gmail/Outlook message ID or social message ID
    thread_id = Column(String(255), index=True)  # For conversation grouping
    source = Column(SQLEnum(MessageSource), default=MessageSource.EMAIL, nullable=False)
    
    # Sender & Recipients
    sender_email = Column(String(255), index=True)
    sender_name = Column(String(255))
    recipient_emails = Column(JSON)  # List of recipient email addresses
    cc_emails = Column(JSON, nullable=True)
    bcc_emails = Column(JSON, nullable=True)
    
    # Content (encrypted)
    subject = Column(String(500))
    encrypted_body = Column(Text, nullable=False)  # AES-256 encrypted
    body_preview = Column(Text)  # First 200 chars for display (unencrypted)
    
    # Metadata
    is_read = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    is_draft = Column(Boolean, default=False)
    has_attachments = Column(Boolean, default=False)
    attachment_count = Column(Integer, default=0)
    
    # AI Analysis Results
    priority = Column(SQLEnum(MessagePriority), nullable=True, index=True)
    category = Column(SQLEnum(MessageCategory), nullable=True, index=True)
    urgency_score = Column(Float, nullable=True)  # 0-100
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    
    # Extracted entities (JSON)
    entities = Column(JSON, default={
        "property_addresses": [],
        "dollar_amounts": [],
        "dates": [],
        "people": [],
        "mls_numbers": []
    })
    
    # AI suggested actions
    suggested_actions = Column(JSON, default=[])  # ["reply", "schedule", "flag_deadline"]
    
    # Vector embedding for semantic search (stored in Pinecone, reference here)
    vector_id = Column(String(255), nullable=True)
    
    # Real estate linking
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    email_account = relationship("EmailAccount", back_populates="messages")
    social_account = relationship("SocialAccount", back_populates="messages")
    property = relationship("Property", back_populates="messages")
    drafts = relationship("Draft", back_populates="original_message")
    tasks = relationship("Task", back_populates="message")
    
    def __repr__(self):
        return f"<Message(id={self.id}, subject={self.subject}, priority={self.priority})>"

