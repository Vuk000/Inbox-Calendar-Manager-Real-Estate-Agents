"""Property model for real estate tracking"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base


class Property(Base):
    """Real estate property for linking emails, tasks, and documents"""
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Property identification
    address = Column(String(500), nullable=False, index=True)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    mls_id = Column(String(100), unique=True, index=True, nullable=True)
    
    # Property details
    property_type = Column(String(50))  # house, condo, land, commercial
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Float, nullable=True)
    square_feet = Column(Integer, nullable=True)
    lot_size = Column(Float, nullable=True)
    year_built = Column(Integer, nullable=True)
    
    # Financial
    list_price = Column(Float, nullable=True)
    sale_price = Column(Float, nullable=True)
    estimated_value = Column(Float, nullable=True)
    
    # Transaction details
    transaction_type = Column(String(50))  # buying, selling, both
    transaction_status = Column(String(50))  # active, pending, closed, cancelled
    
    # Parties involved
    buyer_info = Column(JSON, nullable=True)
    seller_info = Column(JSON, nullable=True)
    agents = Column(JSON, nullable=True)  # List of agent names/emails
    
    # Key dates
    listing_date = Column(DateTime(timezone=True), nullable=True)
    offer_date = Column(DateTime(timezone=True), nullable=True)
    inspection_date = Column(DateTime(timezone=True), nullable=True)
    closing_date = Column(DateTime(timezone=True), nullable=True)
    
    # Documents & Media
    document_urls = Column(JSON, default=[])  # S3 URLs
    photo_urls = Column(JSON, default=[])
    virtual_tour_url = Column(String(500), nullable=True)
    
    # AI-extracted metadata
    metadata = Column(JSON, default={})
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="property")
    tasks = relationship("Task", back_populates="property")
    
    def __repr__(self):
        return f"<Property(id={self.id}, address={self.address}, mls_id={self.mls_id})>"

