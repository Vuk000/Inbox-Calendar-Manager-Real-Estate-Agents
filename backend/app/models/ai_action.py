"""AI Action model for human-in-the-loop confirmations"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db import Base


class AIActionType(str, enum.Enum):
    """Type of AI-proposed action requiring confirmation"""
    MERGE_CONTACTS = "merge_contacts"
    UPDATE_CONTACT = "update_contact"
    CREATE_TRANSACTION = "create_transaction"
    UPDATE_TRANSACTION = "update_transaction"
    LINK_CONTACT_PROPERTY = "link_contact_property"
    SUGGEST_FOLLOW_UP = "suggest_follow_up"


class AIActionStatus(str, enum.Enum):
    """Status of AI action"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"


class AIAction(Base):
    """AI-proposed actions requiring human confirmation (trustworthy AI)"""
    __tablename__ = "ai_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Action details
    action_type = Column(SQLEnum(AIActionType), nullable=False, index=True)
    status = Column(SQLEnum(AIActionStatus), default=AIActionStatus.PENDING, nullable=False, index=True)
    
    # Proposed data (JSON containing the full action details)
    proposed_data = Column(JSON, nullable=False)
    # Example for MERGE_CONTACTS:
    # {
    #   "source_contact_id": 123,
    #   "target_contact_id": 456,
    #   "merge_strategy": "keep_most_recent",
    #   "field_conflicts": {...}
    # }
    
    # AI reasoning
    reason = Column(Text, nullable=False)  # Why the AI is suggesting this action
    confidence_score = Column(Float, nullable=True)  # 0-1 confidence
    
    # Result after execution
    result_data = Column(JSON, nullable=True)  # Result after confirmation
    error_message = Column(String(1000), nullable=True)
    
    # Expiration (actions expire after X days if not confirmed)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="ai_actions")
    
    def __repr__(self):
        return f"<AIAction(id={self.id}, type={self.action_type}, status={self.status})>"

