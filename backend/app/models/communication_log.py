"""Communication log for unified tracking of all interactions"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float, Boolean, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db import Base


class CommunicationType(str, enum.Enum):
    """Type of communication"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PHONE_CALL = "phone_call"
    MEETING = "meeting"
    NOTE = "note"
    TWITTER_DM = "twitter_dm"
    FACEBOOK_MESSENGER = "facebook_messenger"


class CommunicationDirection(str, enum.Enum):
    """Direction of communication"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"


class CommunicationLog(Base):
    """Unified communication log linking all interactions with contacts"""
    __tablename__ = "communication_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User and contact linking
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    
    # Communication details
    communication_type = Column(SQLEnum(CommunicationType), nullable=False, index=True)
    direction = Column(SQLEnum(CommunicationDirection), nullable=False)
    
    # Content
    subject = Column(String(500), nullable=True)
    body = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)  # AI-generated summary
    
    # Metadata
    from_address = Column(String(255), nullable=True)  # Email or phone
    to_address = Column(String(255), nullable=True)
    
    # AI Analysis
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    urgency_score = Column(Float, nullable=True)  # 0-100
    key_topics = Column(JSON, default=[])  # AI-extracted topics
    
    # External references
    external_id = Column(String(255), nullable=True)  # Gmail/Twilio/etc ID
    
    # Related entities
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True, index=True)
    
    # Duration (for calls/meetings)
    duration_seconds = Column(Integer, nullable=True)
    
    # Attachments
    has_attachments = Column(Boolean, default=False)
    attachments = Column(JSON, default=[])  # [{filename, url, size}]
    
    # User actions
    is_starred = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False, index=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Timestamps
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="communications")
    contact = relationship("Contact", back_populates="communications")
    property = relationship("Property", foreign_keys=[property_id])
    transaction = relationship("Transaction", back_populates="communications")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_comm_contact_date', 'contact_id', 'occurred_at'),
        Index('idx_comm_type_direction', 'communication_type', 'direction'),
        Index('idx_comm_user_date', 'user_id', 'occurred_at'),
    )
    
    def __repr__(self):
        return f"<CommunicationLog(id={self.id}, type={self.communication_type}, contact_id={self.contact_id})>"

