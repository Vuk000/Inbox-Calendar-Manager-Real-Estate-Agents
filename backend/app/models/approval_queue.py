"""ApprovalQueue model for human-in-loop feature"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db import Base


class ApprovalFeatureType(str, enum.Enum):
    """Types of features requiring approval"""
    VISION_SCAN = "vision_scan"
    NEIGHBORHOOD_REPORT = "neighborhood_report"
    AI_DRAFT = "ai_draft"
    LEAD_QUALIFICATION = "lead_qualification"


class ApprovalStatus(str, enum.Enum):
    """Approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalQueue(Base):
    """Stores items awaiting human approval (human-in-loop)"""
    __tablename__ = "approval_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Feature info
    feature_type = Column(SQLEnum(ApprovalFeatureType), nullable=False, index=True)
    feature_id = Column(Integer, nullable=True)  # ID of related feature (scan_id, report_id, etc.)
    
    # Data requiring approval (JSONB)
    data = Column(JSON, nullable=False)  # The actual data needing approval
    context = Column(JSON, default={})  # Additional context for approval decision
    
    # Status
    status = Column(
        SQLEnum(ApprovalStatus), 
        default=ApprovalStatus.PENDING, 
        nullable=False, 
        index=True
    )
    
    # Approval details
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Admin/agent who approved
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="approval_queue_items")
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<ApprovalQueue(id={self.id}, feature_type={self.feature_type.value}, status={self.status.value})>"

