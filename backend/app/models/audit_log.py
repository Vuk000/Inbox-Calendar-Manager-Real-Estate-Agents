"""Audit log model for compliance and security"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base


class AuditLog(Base):
    """Audit trail for security and compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    # Actions: login, logout, read_email, send_email, delete_data,
    # export_data, update_settings, etc.
    
    resource_type = Column(String(100), nullable=True)  # email, draft, task, etc.
    resource_id = Column(Integer, nullable=True)
    
    # Context
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    # Request info
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    endpoint = Column(String(500), nullable=True)
    
    # Result
    status = Column(String(50), nullable=True)  # success, failure, error
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"

