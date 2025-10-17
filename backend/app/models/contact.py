"""Contact model for CRM with AI relationship scoring"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base


class Contact(Base):
    """CRM Contact with relationship tracking and AI scoring"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User/Team ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)
    
    # Contact identification
    first_name = Column(String(255), nullable=False, index=True)
    last_name = Column(String(255), nullable=True, index=True)
    company = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    
    # Contact information
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    secondary_phone = Column(String(50), nullable=True)
    
    # Address
    address_line1 = Column(String(500), nullable=True)
    address_line2 = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), default="USA")
    
    # Contact type and status
    contact_type = Column(String(50), nullable=True, index=True)  # buyer, seller, lead, agent, vendor
    contact_status = Column(String(50), default="active", index=True)  # active, inactive, archived
    lead_source = Column(String(100), nullable=True)  # zillow, website, referral, etc.
    
    # AI Relationship Scoring
    relationship_score = Column(Float, default=0.0)  # 0-100
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    contact_frequency = Column(Integer, default=0)  # Number of communications
    
    # Insights (AI-generated)
    ai_insights = Column(JSON, default={
        "summary": "",
        "suggested_actions": [],
        "communication_pattern": "",
        "sentiment_trend": ""
    })
    
    # Preferences and metadata
    preferred_contact_method = Column(String(50), nullable=True)  # email, phone, sms
    tags = Column(JSON, default=[])  # ["hot-lead", "first-time-buyer", etc.]
    custom_fields = Column(JSON, default={})
    
    # Social media
    linkedin_url = Column(String(500), nullable=True)
    facebook_url = Column(String(500), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Sharing
    is_shared_with_team = Column(Boolean, default=False)
    shared_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    shared_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="contacts")
    team = relationship("Team", foreign_keys=[team_id])
    communications = relationship("CommunicationLog", back_populates="contact", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="contact")
    notes_list = relationship("Note", back_populates="contact", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_contact_name', 'first_name', 'last_name'),
        Index('idx_contact_user_status', 'user_id', 'contact_status'),
        Index('idx_contact_type', 'contact_type'),
    )
    
    @property
    def full_name(self):
        """Return full name"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name={self.full_name}, score={self.relationship_score})>"

