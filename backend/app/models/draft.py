"""Draft model for AI-generated email responses

DEPRECATED: This model is kept for backward compatibility only.
New code should handle drafts differently, integrated with CommunicationLog.
The Draft model will be phased out in a future release.
"""
import warnings
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db import Base

# Issue deprecation warning
warnings.warn(
    "Draft model is deprecated. Implement new draft handling with CommunicationLog.",
    DeprecationWarning,
    stacklevel=2
)


class DraftStatus(str, enum.Enum):
    """Draft approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    EDITED = "edited"
    REJECTED = "rejected"
    SENT = "sent"


class Draft(Base):
    """AI-generated email drafts with human-in-the-loop"""
    __tablename__ = "drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    communication_log_id = Column(Integer, ForeignKey("communication_logs.id"), nullable=True, index=True)
    
    # Draft content
    subject = Column(String(500))
    generated_content = Column(Text, nullable=False)
    final_content = Column(Text, nullable=True)  # After human edits
    
    # AI metadata
    confidence_score = Column(Float, nullable=True)  # 0-1
    generation_prompt = Column(Text, nullable=True)  # Prompt used
    model_version = Column(String(100))
    
    # Alternative drafts (for A/B options)
    variant_number = Column(Integer, default=1)  # 1, 2, 3 for multiple suggestions
    
    # Human feedback
    approval_status = Column(SQLEnum(DraftStatus), default=DraftStatus.PENDING, nullable=False)
    human_edits = Column(JSON, nullable=True)  # Track what was changed for learning
    feedback_notes = Column(Text, nullable=True)
    
    # Context used for generation
    context_data = Column(JSON, nullable=True)  # CRM data, market data, etc.
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="drafts")
    communication_log = relationship("CommunicationLog", foreign_keys=[communication_log_id])
    
    def __repr__(self):
        return f"<Draft(id={self.id}, status={self.approval_status}, confidence={self.confidence_score})>"

