"""Transaction model for deal pipeline management"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float, Boolean, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db import Base


class TransactionStage(str, enum.Enum):
    """Pipeline stages for transactions"""
    LEAD = "lead"
    ACTIVE = "active"
    PENDING = "pending"
    UNDER_CONTRACT = "under_contract"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    ARCHIVED = "archived"


class TransactionType(str, enum.Enum):
    """Type of real estate transaction"""
    BUYER = "buyer"
    SELLER = "seller"
    BOTH = "both"
    LEASE = "lease"
    REFERRAL = "referral"


class Transaction(Base):
    """Real estate transaction/deal with pipeline management"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    
    # Transaction identification
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    
    # Pipeline management
    stage = Column(SQLEnum(TransactionStage), default=TransactionStage.LEAD, nullable=False, index=True)
    pipeline_position = Column(Integer, default=0)  # For ordering in Kanban
    
    # Linked entities
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    
    # Financial details
    estimated_value = Column(Float, nullable=True)
    commission_percentage = Column(Float, nullable=True)
    estimated_commission = Column(Float, nullable=True)
    actual_sale_price = Column(Float, nullable=True)
    actual_commission = Column(Float, nullable=True)
    
    # Checklist system
    checklist_template = Column(String(50), default="buyer")  # buyer, seller, both
    checklist_items = Column(JSON, default=[])  # [{id, title, completed, due_date, completed_at}]
    
    # Timeline events
    timeline_events = Column(JSON, default=[])  # [{date, title, description, type}]
    
    # Key dates
    lead_date = Column(DateTime(timezone=True), nullable=True)
    contract_date = Column(DateTime(timezone=True), nullable=True)
    inspection_date = Column(DateTime(timezone=True), nullable=True)
    appraisal_date = Column(DateTime(timezone=True), nullable=True)
    closing_date = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Probability and scoring
    probability = Column(Float, default=50.0)  # 0-100%
    ai_confidence_score = Column(Float, nullable=True)  # AI prediction of success
    
    # Sharing and collaboration
    is_shared = Column(Boolean, default=False)
    public_timeline_uuid = Column(String(36), nullable=True, unique=True, index=True)  # For shareable link
    
    # Notes and metadata
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=[])
    custom_fields = Column(JSON, default={})
    
    # Loss/win reason
    outcome_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    team = relationship("Team", foreign_keys=[team_id])
    contact = relationship("Contact", back_populates="transactions")
    property = relationship("Property", back_populates="transactions")
    tasks = relationship("Task", back_populates="transaction", cascade="all, delete-orphan")
    communications = relationship("CommunicationLog", back_populates="transaction")
    notes_list = relationship("Note", back_populates="transaction", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_transaction_stage', 'stage'),
        Index('idx_transaction_user_stage', 'user_id', 'stage'),
        Index('idx_transaction_contact', 'contact_id'),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, title={self.title}, stage={self.stage})>"

