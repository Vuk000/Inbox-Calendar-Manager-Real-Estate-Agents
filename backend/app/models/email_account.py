"""Email account model for Gmail/Outlook integration"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db import Base


class EmailProvider(str, enum.Enum):
    """Email provider enumeration"""
    GMAIL = "gmail"
    OUTLOOK = "outlook"


class SyncStatus(str, enum.Enum):
    """Email sync status"""
    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"
    PAUSED = "paused"


class EmailAccount(Base):
    """Email account with encrypted OAuth tokens"""
    __tablename__ = "email_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Provider details
    provider = Column(SQLEnum(EmailProvider), nullable=False)
    email_address = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255))
    
    # Encrypted OAuth credentials (AES-256)
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Sync configuration
    sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.IDLE)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_error_message = Column(Text, nullable=True)
    sync_cursor = Column(String(255), nullable=True)  # For incremental sync
    
    # Gmail-specific
    gmail_history_id = Column(String(255), nullable=True)
    gmail_watch_expiration = Column(DateTime(timezone=True), nullable=True)
    
    # Outlook-specific
    outlook_subscription_id = Column(String(255), nullable=True)
    outlook_delta_token = Column(String(255), nullable=True)
    
    # Settings
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    auto_sync_enabled = Column(Boolean, default=True)
    sync_interval_minutes = Column(Integer, default=5)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="email_accounts")
    # Messages are now tracked in CommunicationLog via external_id
    
    def __repr__(self):
        return f"<EmailAccount(id={self.id}, email={self.email_address}, provider={self.provider})>"

