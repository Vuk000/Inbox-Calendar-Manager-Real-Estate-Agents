"""Team collaboration API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from ..db import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.team import Team, TeamMember
from ..models.contact import Contact
from ..models.communication_log import CommunicationLog

router = APIRouter(prefix="/teams", tags=["Teams"])


# Pydantic schemas
class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    logo_url: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, max_length=500)
    settings: dict = {}


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    logo_url: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, max_length=500)
    settings: Optional[dict] = None
    is_active: Optional[bool] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    settings: dict
    logo_url: Optional[str]
    website: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    role: str
    status: str
    invited_at: datetime
    joined_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TeamWithMembersResponse(TeamResponse):
    members: List[TeamMemberResponse] = []


class InviteMemberRequest(BaseModel):
    user_email: EmailStr
    role: str = Field("member", pattern="^(member|admin)$")


class ActivityResponse(BaseModel):
    timestamp: datetime
    user_id: int
    user_name: str
    activity_type: str
    description: str
    entity_type: Optional[str]
    entity_id: Optional[int]


# Endpoints
@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new team (user becomes owner)"""
    # Check if user already owns a team
    existing_team = db.query(Team).filter(Team.owner_id == current_user.id).first()
    if existing_team:
        raise HTTPException(
            status_code=400,
            detail="User already owns a team. Each user can own only one team."
        )
    
    team = Team(
        owner_id=current_user.id,
        **team_data.model_dump()
    )
    
    db.add(team)
    db.commit()
    db.refresh(team)
    
    return team


@router.get("/{team_id}", response_model=TeamWithMembersResponse)
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team details"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user is owner or member
    is_owner = team.owner_id == current_user.id
    is_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.status == "active"
    ).first() is not None
    
    if not (is_owner or is_member):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return team


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update team details (owner only)"""
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.owner_id == current_user.id
    ).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or access denied")
    
    update_data = team_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team, key, value)
    
    team.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(team)
    
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete team (owner only)"""
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.owner_id == current_user.id
    ).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or access denied")
    
    db.delete(team)
    db.commit()


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    team_id: int,
    invite_request: InviteMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite a member to the team (owner only)"""
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.owner_id == current_user.id
    ).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or access denied")
    
    # Find user by email
    invited_user = db.query(User).filter(User.email == invite_request.user_email).first()
    if not invited_user:
        raise HTTPException(status_code=404, detail="User not found with that email")
    
    # Check if already a member
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == invited_user.id
    ).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a team member")
    
    # Create team member
    member = TeamMember(
        team_id=team_id,
        user_id=invited_user.id,
        role=invite_request.role,
        status="invited",
        invited_by=current_user.id,
        invited_at=datetime.utcnow()
    )
    
    db.add(member)
    db.commit()
    db.refresh(member)
    
    # TODO: Send invitation email
    
    return member


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List team members"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user is owner or member
    is_owner = team.owner_id == current_user.id
    is_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.status == "active"
    ).first() is not None
    
    if not (is_owner or is_member):
        raise HTTPException(status_code=403, detail="Access denied")
    
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    return members


@router.delete("/{team_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    team_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from the team (owner only)"""
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.owner_id == current_user.id
    ).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or access denied")
    
    member = db.query(TeamMember).filter(
        TeamMember.id == member_id,
        TeamMember.team_id == team_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    db.delete(member)
    db.commit()


@router.get("/{team_id}/activity", response_model=List[ActivityResponse])
async def get_team_activity(
    team_id: int,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unified activity timeline for team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user is owner or member
    is_owner = team.owner_id == current_user.id
    is_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.status == "active"
    ).first() is not None
    
    if not (is_owner or is_member):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get shared contacts
    shared_contacts = db.query(Contact).filter(
        Contact.team_id == team_id,
        Contact.is_shared_with_team == True
    ).all()
    
    contact_ids = [c.id for c in shared_contacts]
    
    # Get recent communications for shared contacts
    communications = db.query(CommunicationLog).filter(
        CommunicationLog.contact_id.in_(contact_ids)
    ).order_by(
        CommunicationLog.occurred_at.desc()
    ).limit(limit).all()
    
    # Build activity timeline
    activity = []
    for comm in communications:
        user = db.query(User).filter(User.id == comm.user_id).first()
        contact = db.query(Contact).filter(Contact.id == comm.contact_id).first()
        
        activity.append({
            "timestamp": comm.occurred_at,
            "user_id": comm.user_id,
            "user_name": user.full_name if user else "Unknown",
            "activity_type": f"{comm.communication_type.value}_communication",
            "description": f"Contacted {contact.full_name if contact else 'contact'} via {comm.communication_type.value}",
            "entity_type": "communication",
            "entity_id": comm.id
        })
    
    return activity

