"""Analytics model for tracking user metrics"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base


class Analytics(Base):
    """Analytics and metrics tracking"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Metric details
    metric_type = Column(String(100), nullable=False, index=True)
    # Types: emails_processed, time_saved, leads_qualified, tasks_created,
    # drafts_generated, drafts_sent, urgents_flagged, etc.
    
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)  # hours, count, percentage
    
    # Context
    metadata = Column(JSON, nullable=True)  # Additional context
    
    # Date aggregation
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    week_start = Column(DateTime(timezone=True), nullable=True, index=True)
    month_start = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analytics")
    
    def __repr__(self):
        return f"<Analytics(id={self.id}, type={self.metric_type}, value={self.metric_value})>"

