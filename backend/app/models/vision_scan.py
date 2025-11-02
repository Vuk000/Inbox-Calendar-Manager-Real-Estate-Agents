"""VisionScan model for VisionHome AI feature"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base


class VisionScan(Base):
    """Stores property scan results from VisionHome AI"""
    __tablename__ = "vision_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Image info
    image_url = Column(String(500), nullable=False)  # S3 URL or external URL
    image_filename = Column(String(255), nullable=True)
    
    # Analysis results (JSONB)
    matches = Column(JSON, default=[])  # Array of matched properties from Zillow
    renovations = Column(JSON, default={})  # Renovation suggestions with overlays
    vision_labels = Column(JSON, default=[])  # Google Vision detected labels
    rooms_detected = Column(JSON, default=[])  # Detected rooms and features
    
    # Metadata
    property_address = Column(String(255), nullable=True)  # If address provided
    property_type = Column(String(50), nullable=True)  # house, condo, apartment, etc.
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="vision_scans")
    
    def __repr__(self):
        return f"<VisionScan(id={self.id}, user_id={self.user_id}, status={self.status})>"

