"""Team model for collaboration and brokerage management"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base


class Team(Base):
    """Team model for real estate team/brokerage collaboration"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Team identification
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    
    # Owner relationship (one-to-one with User)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Team settings
    settings = Column(JSON, default={
        "shared_contacts": True,
        "shared_transactions": True,
        "activity_notifications": True,
        "member_permissions": {
            "can_edit_contacts": False,
            "can_delete_contacts": False,
            "can_view_communications": True,
            "can_add_notes": True
        }
    })
    
    # Branding (optional)
    logo_url = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_team", foreign_keys=[owner_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, owner_id={self.owner_id})>"


class TeamMember(Base):
    """Team member association with role"""
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Role and status
    role = Column(String(50), default="member")  # member, admin
    status = Column(String(50), default="active")  # active, invited, suspended
    
    # Invitation
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    joined_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], back_populates="team_memberships")
    inviter = relationship("User", foreign_keys=[invited_by])
    
    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role={self.role})>"

