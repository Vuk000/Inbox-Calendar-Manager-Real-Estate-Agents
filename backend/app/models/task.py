"""Task model for action items from emails"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    
    # Task details
    task_type = Column(SQLEnum(TaskType), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling
    due_date = Column(DateTime(timezone=True), nullable=True)
    due_time = Column(String(20), nullable=True)  # HH:MM format
    reminder_at = Column(DateTime(timezone=True), nullable=True)
    
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    message = relationship("Message", back_populates="tasks")
    property = relationship("Property", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, type={self.task_type}, status={self.status})>"

