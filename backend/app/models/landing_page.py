"""Landing page model for lead generation"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base


class LandingPage(Base):
    """IDX landing page for lead generation with SEO optimization"""
    __tablename__ = "landing_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Page identification
    slug = Column(String(255), nullable=False, unique=True, index=True)
    title = Column(String(500), nullable=False)
    
    # Template and design
    template = Column(String(100), default="modern-hero")  # modern-hero, minimalist, luxury, etc.
    
    # SEO
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(Text, nullable=True)
    seo_keywords = Column(JSON, default=[])
    
    # Content
    hero_image = Column(String(500), nullable=True)
    hero_title = Column(String(500), nullable=True)
    hero_subtitle = Column(Text, nullable=True)
    cta_text = Column(String(100), default="Get Started")
    cta_button_color = Column(String(50), default="#2563eb")
    
    # Form configuration
    form_fields = Column(JSON, default=[
        {"name": "name", "type": "text", "label": "Full Name", "required": True},
        {"name": "email", "type": "email", "label": "Email", "required": True},
        {"name": "phone", "type": "tel", "label": "Phone", "required": False},
        {"name": "message", "type": "textarea", "label": "Message", "required": False}
    ])
    
    # Additional sections
    sections = Column(JSON, default=[])  # [{type: "features", content: {...}}, ...]
    
    # Publishing
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Analytics
    views_count = Column(Integer, default=0)
    leads_count = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    analytics = Column(JSON, default={
        "daily_views": {},
        "daily_leads": {},
        "traffic_sources": {}
    })
    
    # Custom CSS/JS (advanced)
    custom_css = Column(Text, nullable=True)
    custom_js = Column(Text, nullable=True)
    
    # Integration settings
    webhook_url = Column(String(500), nullable=True)  # Send leads to external system
    thank_you_message = Column(Text, nullable=True)
    redirect_url = Column(String(500), nullable=True)  # After form submission
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="landing_pages")
    
    # Indexes
    __table_args__ = (
        Index('idx_landing_page_slug', 'slug'),
        Index('idx_landing_page_published', 'is_published'),
    )
    
    def __repr__(self):
        return f"<LandingPage(id={self.id}, slug={self.slug}, published={self.is_published})>"

