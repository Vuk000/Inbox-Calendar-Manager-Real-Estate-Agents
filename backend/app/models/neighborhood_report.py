"""NeighborhoodReport model for Neighborhood Whisper feature"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base


class NeighborhoodReport(Base):
    """Stores neighborhood analysis results from Neighborhood Whisper"""
    __tablename__ = "neighborhood_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Query info
    query = Column(String(500), nullable=False)  # Original search query
    location = Column(String(255), nullable=False)  # Parsed location (address, zip, city)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Scores and metrics
    fit_score = Column(Numeric(5, 2), nullable=True)  # 0.00 to 100.00
    amenities_score = Column(Numeric(5, 2), nullable=True)
    sentiment_score = Column(Numeric(5, 2), nullable=True)  # From reviews
    eco_score = Column(Numeric(5, 2), nullable=True)  # Environmental/eco-friendliness
    
    # Forecast data (JSONB)
    forecast = Column(JSON, default={})  # Market trends, predictions
    # Structure: {"price_trend": "up", "growth_rate": 5.2, "months": 12, ...}
    
    # Eco ROI
    eco_roi = Column(Numeric(10, 2), nullable=True)  # Estimated ROI for eco investments
    
    # Additional data
    review_insights = Column(JSON, default=[])  # Parsed review insights
    similar_neighborhoods = Column(JSON, default=[])  # Similar neighborhoods from ML
    market_data = Column(JSON, default={})  # Market statistics
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="neighborhood_reports")
    
    # Performance indexes
    __table_args__ = (
        Index('idx_neighborhood_user_status', 'user_id', 'status'),
        Index('idx_neighborhood_zip', 'zip_code'),
        Index('idx_neighborhood_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<NeighborhoodReport(id={self.id}, user_id={self.user_id}, fit_score={self.fit_score})>"

