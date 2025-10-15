"""
Shared Pydantic types and schemas
Centralized type definitions for consistency across the application
"""
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator


# Email-related types
class EmailContent(BaseModel):
    """Email content structure"""
    subject: str
    body: str
    sender_email: EmailStr
    sender_name: Optional[str] = None
    received_at: str
    thread_context: Optional[str] = None
    external_id: Optional[str] = None


class EmailEntities(BaseModel):
    """Extracted entities from email"""
    property_addresses: List[str] = Field(default_factory=list)
    dollar_amounts: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    people: List[str] = Field(default_factory=list)
    mls_numbers: List[str] = Field(default_factory=list)


EmailPriority = Literal["high", "medium", "low"]
EmailCategory = Literal[
    "offer", "counteroffer", "lead", "inspection", "closing",
    "showing_request", "negotiation", "general", "newsletter", "spam"
]
SuggestedAction = Literal[
    "reply", "schedule", "flag_deadline", "contact_crm", "forward", "archive"
]


class TriageResult(BaseModel):
    """Triage analysis result"""
    priority: EmailPriority
    urgency_score: float = Field(ge=0, le=100)
    category: EmailCategory
    entities: EmailEntities
    suggested_actions: List[SuggestedAction]
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    key_points: List[str]
    deadline_detected: Optional[str] = None
    requires_urgent_response: bool
    confidence: float = Field(ge=0, le=1)
    model_version: str
    analyzed_at: str
    error: Optional[str] = None


# Draft-related types
class DraftVariant(BaseModel):
    """Single draft variant"""
    variant_number: int
    content: str
    confidence_score: float = Field(ge=0, le=1)
    generated_at: str
    model_version: Optional[str] = None
    word_count: int = 0
    has_call_to_action: bool = False
    error: Optional[str] = None


class AgentInfo(BaseModel):
    """Agent information for draft generation"""
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    brokerage: Optional[str] = None


# Lead qualification types
BuyerOrSeller = Literal["buyer", "seller", "both", "unknown"]
UrgencyLevel = Literal["high", "medium", "low"]
LeadIntent = Literal["buy", "sell", "rent", "invest", "explore", "spam"]
ContactMethod = Literal["email", "phone", "text", "unknown"]


class QualificationFactors(BaseModel):
    """Lead qualification factors"""
    budget_mentioned: bool = False
    budget_range: Optional[str] = None
    timeline_mentioned: bool = False
    timeline: Optional[str] = None
    location_specified: bool = False
    locations: List[str] = Field(default_factory=list)
    buyer_or_seller: BuyerOrSeller = "unknown"
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    specific_features: List[str] = Field(default_factory=list)
    pre_approved: Optional[bool] = None
    working_with_agent: Optional[bool] = None
    urgency_level: UrgencyLevel = "medium"


class ContactInfo(BaseModel):
    """Lead contact information"""
    phone_mentioned: bool = False
    phone_number: Optional[str] = None
    preferred_contact_method: ContactMethod = "unknown"
    best_time_to_contact: Optional[str] = None


class IntentAnalysis(BaseModel):
    """Lead intent analysis"""
    primary_intent: LeadIntent
    motivation: Optional[str] = None
    pain_points: List[str] = Field(default_factory=list)
    objections: List[str] = Field(default_factory=list)


LeadAction = Literal[
    "call_immediately", "send_listings", "schedule_showing",
    "send_market_report", "ask_qualifying_questions", "nurture_campaign", "ignore"
]


class LeadQualification(BaseModel):
    """Complete lead qualification result"""
    lead_score: int = Field(ge=0, le=100)
    qualification_factors: QualificationFactors
    contact_info: Optional[ContactInfo] = None
    intent_analysis: Optional[IntentAnalysis] = None
    recommended_actions: List[LeadAction]
    auto_response_suggested: bool = False
    crm_tags: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    qualified_at: str
    model_version: Optional[str] = None
    source_email: Optional[str] = None
    error: Optional[str] = None


# Task-related types
TaskStatus = Literal["pending", "in_progress", "completed", "cancelled"]
TaskPriority = Literal["high", "medium", "low"]


class TaskCreate(BaseModel):
    """Task creation schema"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = "pending"
    priority: TaskPriority = "medium"
    due_date: Optional[datetime] = None
    email_id: Optional[int] = None
    assigned_to: Optional[int] = None


class TaskUpdate(BaseModel):
    """Task update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Property-related types
PropertyStatus = Literal["active", "pending", "sold", "withdrawn"]


class PropertyBase(BaseModel):
    """Base property schema"""
    address: str
    city: str
    state: str
    zip_code: str
    price: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    bathrooms: float = Field(ge=0)
    square_feet: Optional[int] = Field(None, ge=0)
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    property_type: Optional[str] = None
    status: PropertyStatus = "active"
    mls_number: Optional[str] = None


# User-related types
UserRole = Literal["agent", "admin", "viewer"]
SubscriptionTier = Literal["solo", "professional", "enterprise"]


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str
    role: UserRole = "agent"
    is_active: bool = True
    subscription_tier: SubscriptionTier = "solo"


# API Response types
class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List[Any]
    total: int
    page: int = 1
    page_size: int = 20
    has_next: bool = False
    has_prev: bool = False


# Analytics types
class ProductivityMetrics(BaseModel):
    """Productivity analytics"""
    emails_triaged: int = 0
    time_saved_hours: float = 0.0
    lead_conversion_rate: float = 0.0
    response_time_avg_hours: float = 0.0
    period: str = "30d"


class ROIMetrics(BaseModel):
    """ROI calculation metrics"""
    roi_monthly: float = 0.0
    time_saved_hours: float = 0.0
    hourly_rate: float = 0.0
    subscription_cost: float = 0.0
    net_value: float = 0.0


# WebSocket message types
class WebSocketMessage(BaseModel):
    """WebSocket message structure"""
    type: str  # 'new_email', 'triage_complete', 'draft_ready', etc.
    payload: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Error response types
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

