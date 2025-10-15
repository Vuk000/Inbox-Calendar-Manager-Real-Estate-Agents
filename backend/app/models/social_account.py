"""Social account model for multi-channel integrations"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..db import Base


class SocialProvider(str, enum.Enum):
    TWITTER = "twitter"
    FACEBOOK_MESSENGER = "facebook_messenger"


class SocialAccount(Base):
    """Stores social media channel credentials per user."""

    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    provider = Column(SQLEnum(SocialProvider), nullable=False)
    handle = Column(String(255), nullable=False)
    display_name = Column(String(255))
    external_id = Column(String(255), nullable=True)

    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)

    page_id = Column(String(255), nullable=True)  # For Facebook pages
    extra_metadata = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    auto_sync_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="social_accounts")
    messages = relationship("Message", back_populates="social_account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SocialAccount(id={self.id}, provider={self.provider}, handle={self.handle})>"
