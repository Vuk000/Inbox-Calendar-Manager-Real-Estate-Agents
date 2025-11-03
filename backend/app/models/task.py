"""Task model for action items from emails"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Index
import enum
from ..db import Base


class TaskType(str, enum.Enum):
    """Task type enumeration"""
    SHOWING = "showing"
    INSPECTION = "inspection"
    APPRAISAL = "appraisal"
    SIGNING = "signing"
    FOLLOW_UP = "follow_up"
    DEADLINE = "deadline"
    CALL = "call"
    GENERAL = "general"


class TaskStatus(str, enum.Enum):
    """Task status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Task(Base):
    """Task model for converting emails to actions"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    communication_log_id = Column(Integer, ForeignKey("communication_logs.id"), nullable=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    
    # Task details
    task_type = Column(SQLEnum(TaskType), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling (Calendar Event Support)
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)  # Start date/time for calendar events
    due_time = Column(String(20), nullable=True)  # HH:MM format
    end_date = Column(DateTime(timezone=True), nullable=True)  # End date/time for calendar events
    reminder_at = Column(DateTime(timezone=True), nullable=True)
    
    # AI Features
    ai_suggested = Column(Boolean, default=False, index=True)  # Whether this event was AI-suggested
    ai_confidence = Column(Numeric(5, 2), nullable=True)  # Confidence score for AI suggestions
    
    # Assignment (for teams)
    assigned_to_email = Column(String(255), nullable=True)
    assigned_to_name = Column(String(255), nullable=True)
    
    # Status
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high
    
    # Integration
    calendar_event_id = Column(String(255), nullable=True)  # Google Calendar ID
    external_task_id = Column(String(255), nullable=True)  # Asana, Todoist, etc.
    
    # Completion
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completion_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    communication_log = relationship("CommunicationLog", foreign_keys=[communication_log_id])
    property = relationship("Property", back_populates="tasks")
    transaction = relationship("Transaction", back_populates="tasks")
    contact = relationship("Contact", foreign_keys=[contact_id])
    
    # Performance indexes
    __table_args__ = (
        Index('idx_task_user_due', 'user_id', 'due_date'),
        Index('idx_task_status_type', 'status', 'task_type'),
        Index('idx_task_ai_suggested', 'ai_suggested', 'user_id'),
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, type={self.task_type}, status={self.status})>"

