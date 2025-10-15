/**
 * API Response Types
 * TypeScript interfaces for all API endpoints
 */

// Common types
export type Priority = 'high' | 'medium' | 'low'
export type EmailCategory = 
  | 'offer' 
  | 'counteroffer' 
  | 'lead' 
  | 'inspection' 
  | 'closing' 
  | 'showing_request' 
  | 'negotiation' 
  | 'general' 
  | 'newsletter' 
  | 'spam'

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled'
export type TaskPriority = 'high' | 'medium' | 'low'
export type UserRole = 'agent' | 'admin' | 'viewer'
export type SubscriptionTier = 'solo' | 'professional' | 'enterprise'

// Pagination
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_next: boolean
  has_prev: boolean
}

// Auth
export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
}

export interface User {
  id: number
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  subscription_tier: SubscriptionTier
  created_at: string
  updated_at?: string
}

// Emails
export interface EmailEntities {
  property_addresses: string[]
  dollar_amounts: string[]
  dates: string[]
  people: string[]
  mls_numbers: string[]
}

export interface Email {
  id: number
  subject: string
  sender_email: string
  sender_name: string
  body?: string
  body_preview: string
  received_at: string
  priority: Priority
  category: EmailCategory
  urgency_score: number
  sentiment_score?: number
  is_read: boolean
  is_starred: boolean
  has_attachments: boolean
  attachment_count: number
  entities?: EmailEntities
  suggested_actions?: string[]
  triage_data?: TriageResult
  processed_at?: string
}

export interface TriageResult {
  priority: Priority
  urgency_score: number
  category: EmailCategory
  entities: EmailEntities
  suggested_actions: string[]
  sentiment_score: number
  key_points: string[]
  deadline_detected: string | null
  requires_urgent_response: boolean
  confidence: number
  model_version: string
  analyzed_at: string
  error?: string
}

// Drafts
export interface DraftVariant {
  variant_number: number
  content: string
  confidence_score: number
  generated_at: string
  model_version?: string
  word_count: number
  has_call_to_action: boolean
  error?: string
}

export interface Draft {
  id: number
  email_id: number
  variants: DraftVariant[]
  selected_variant?: number
  status: 'pending' | 'approved' | 'rejected' | 'sent'
  created_at: string
  approved_at?: string
  sent_at?: string
}

export interface GenerateDraftRequest {
  email_id: number
  num_variants?: number
  style_examples?: string[]
  context?: Record<string, any>
}

export interface ApproveDraftRequest {
  edited_content?: string
  send: boolean
}

// Tasks
export interface Task {
  id: number
  title: string
  description?: string
  status: TaskStatus
  priority: TaskPriority
  due_date?: string
  completed_at?: string
  email_id?: number
  assigned_to?: number
  created_by: number
  created_at: string
  updated_at: string
}

export interface CreateTaskRequest {
  title: string
  description?: string
  priority?: TaskPriority
  due_date?: string
  email_id?: number
}

export interface UpdateTaskRequest {
  title?: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
  due_date?: string
}

// Properties
export interface Property {
  id: number
  address: string
  city: string
  state: string
  zip_code: string
  price: number
  bedrooms: number
  bathrooms: number
  square_feet?: number
  lot_size?: number
  year_built?: number
  property_type?: string
  status: 'active' | 'pending' | 'sold' | 'withdrawn'
  mls_number?: string
  images?: string[]
  created_at: string
  updated_at: string
}

// Analytics
export interface ProductivityMetrics {
  emails_triaged: number
  time_saved_hours: number
  lead_conversion_rate: number
  response_time_avg_hours: number
  period: string
}

export interface ROIMetrics {
  roi_monthly: number
  time_saved_hours: number
  hourly_rate: number
  subscription_cost: number
  net_value: number
}

export interface AnalyticsOverview {
  emails_processed: number
  drafts_generated: number
  tasks_completed: number
  time_saved_hours: number
  lead_conversion_rate: number
  avg_response_time_hours: number
}

// Integrations
export interface IntegrationStatus {
  gmail?: {
    connected: boolean
    last_sync: string | null
    email?: string
  }
  outlook?: {
    connected: boolean
    last_sync: string | null
    email?: string
  }
  twilio?: {
    connected: boolean
    last_sync: string | null
  }
}

export interface ConnectIntegrationRequest {
  provider: 'gmail' | 'outlook' | 'twilio'
  credentials?: Record<string, string>
}

// WebSocket
export interface WebSocketMessage<T = any> {
  type: string
  payload: T
  timestamp: string
}

export interface NewEmailEvent {
  email: Email
  user_id: number
}

export interface TriageCompleteEvent {
  email_id: number
  triage_result: TriageResult
}

export interface DraftReadyEvent {
  draft_id: number
  email_id: number
}

// Errors
export interface ErrorResponse {
  detail: string
  error_code?: string
  timestamp: string
}

// Lead Qualification
export interface QualificationFactors {
  budget_mentioned: boolean
  budget_range?: string
  timeline_mentioned: boolean
  timeline?: string
  location_specified: boolean
  locations: string[]
  buyer_or_seller: 'buyer' | 'seller' | 'both' | 'unknown'
  property_type?: string
  bedrooms?: number
  bathrooms?: number
  specific_features: string[]
  pre_approved?: boolean
  working_with_agent?: boolean
  urgency_level: 'high' | 'medium' | 'low'
}

export interface LeadQualification {
  lead_score: number
  qualification_factors: QualificationFactors
  contact_info?: {
    phone_mentioned: boolean
    phone_number?: string
    preferred_contact_method: 'email' | 'phone' | 'text' | 'unknown'
    best_time_to_contact?: string
  }
  intent_analysis?: {
    primary_intent: 'buy' | 'sell' | 'rent' | 'invest' | 'explore' | 'spam'
    motivation?: string
    pain_points: string[]
    objections: string[]
  }
  recommended_actions: string[]
  auto_response_suggested: boolean
  crm_tags: string[]
  confidence: number
  qualified_at: string
  error?: string
}

