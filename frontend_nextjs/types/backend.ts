/**
 * Type definitions matching backend models
 * These types ensure type safety between frontend and backend
 */

// Communication Types
export type CommunicationType = 'email' | 'sms' | 'phone' | 'meeting' | 'note';

export interface CommunicationLog {
  id: number;
  user_id: number;
  contact_id: number;
  communication_type: CommunicationType;
  from_address?: string | null;
  to_address?: string | null;
  subject?: string | null;
  summary?: string | null;
  body?: string | null;
  occurred_at: string;
  is_starred: boolean;
  is_archived: boolean;
  is_deleted: boolean;
  urgency_score?: number | null;
  sentiment_score?: number | null;
  thread_id?: string | null;
  message_id?: string | null;
  created_at: string;
  updated_at?: string | null;
}

// Email type (matches backend EmailListResponse)
// Note: Backend returns EmailListResponse which is a subset of CommunicationLog
export interface Email {
  id: number;
  subject?: string | null;
  from_address: string;
  summary?: string | null;
  urgency_score?: number | null;
  sentiment_score?: number | null;
  has_attachments?: boolean;
  occurred_at: string;
  contact_id: number;
  is_starred: boolean;
  is_archived: boolean;
  // Additional fields that may be present
  body?: string | null;
  to_address?: string | null;
  thread_id?: string | null;
  created_at?: string;
}

// Task Types
export type TaskType = 'showing' | 'inspection' | 'appraisal' | 'signing' | 'follow_up' | 'deadline' | 'call' | 'general';
export type TaskStatus = 'todo' | 'in_progress' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: number;
  user_id: number;
  title: string;
  description?: string | null;
  task_type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string | null;
  due_time?: string | null;
  completion_notes?: string | null;
  message_id?: number | null;
  property_id?: number | null;
  created_at: string;
  updated_at?: string | null;
}

// Contact Types
export interface Contact {
  id: number;
  user_id: number;
  team_id?: number | null;
  first_name: string;
  last_name?: string | null;
  full_name?: string;
  email?: string | null;
  phone?: string | null;
  phone_number?: string | null;
  company?: string | null;
  job_title?: string | null;
  address?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  state?: string | null;
  zip_code?: string | null;
  country?: string | null;
  notes?: string | null;
  tags?: string[] | null;
  is_shared_with_team: boolean;
  created_at: string;
  updated_at?: string | null;
}

// Draft Types
export type DraftStatus = 'pending' | 'approved' | 'sent' | 'rejected';

export interface Draft {
  id: number;
  user_id: number;
  communication_log_id: number;
  content: string;
  status: DraftStatus;
  confidence_score?: number | null;
  feedback?: string | null;
  generated_at: string;
  sent_at?: string | null;
  created_at: string;
  updated_at?: string | null;
}

// Transaction Types
export type TransactionType = 'buyer' | 'seller' | 'both' | 'lease' | 'referral';
export type TransactionStage = 'lead' | 'active' | 'pending' | 'under_contract' | 'closed_won' | 'closed_lost' | 'archived';

export interface Transaction {
  id: number;
  user_id: number;
  team_id?: number | null;
  title: string;
  description?: string | null;
  transaction_type: TransactionType;
  stage: TransactionStage;
  contact_id: number;
  property_id?: number | null;
  estimated_value?: number | null;
  commission_percentage?: number | null;
  estimated_commission?: number | null;
  probability: number;
  lead_date?: string | null;
  contract_date?: string | null;
  closing_date?: string | null;
  closed_at?: string | null;
  is_shared: boolean;
  public_timeline_uuid?: string | null;
  notes?: string | null;
  tags: string[];
  created_at: string;
  updated_at?: string | null;
}

// Property Types
export interface Property {
  id: number;
  address: string;
  city?: string | null;
  state?: string | null;
  zip_code?: string | null;
  mls_id?: string | null;
  property_type?: string | null;
  list_price?: number | null;
  sale_price?: number | null;
  transaction_type?: string | null;
  transaction_status?: string | null;
  closing_date?: string | null;
  created_at: string;
}

// Team Types
export interface Team {
  id: number;
  name: string;
  description?: string | null;
  owner_id: number;
  settings: Record<string, any>;
  logo_url?: string | null;
  website?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at?: string | null;
  members?: TeamMember[];
}

export interface TeamMember {
  id: number;
  team_id: number;
  user_id: number;
  role: 'member' | 'admin';
  status: 'invited' | 'active' | 'inactive';
  invited_at: string;
  joined_at?: string | null;
}

// AI Action Types
export type AIActionType = 'contact_merge' | 'draft_generation' | 'task_creation' | 'email_send' | 'contact_creation';
export type AIActionStatus = 'pending' | 'confirmed' | 'rejected' | 'expired' | 'executed';

export interface AIAction {
  id: number;
  user_id: number;
  action_type: AIActionType;
  status: AIActionStatus;
  proposed_data: Record<string, any>;
  reason: string;
  confidence_score?: number | null;
  result_data?: Record<string, any> | null;
  error_message?: string | null;
  expires_at: string;
  created_at: string;
  confirmed_at?: string | null;
  executed_at?: string | null;
}

// Integration Types
export interface EmailAccount {
  id: number;
  user_id: number;
  provider: string;
  email_address: string;
  is_active: boolean;
  is_primary: boolean;
  sync_status: string;
  last_sync_at?: string | null;
  created_at: string;
}

export interface SocialAccount {
  id: number;
  user_id: number;
  provider: string;
  handle: string;
  display_name?: string | null;
  is_active: boolean;
  created_at: string;
}

// Analytics Types
export interface DashboardMetrics {
  emails_processed_today: number;
  tasks_completed: number;
  drafts_generated: number;
  time_saved_hours: number;
  email_activity?: {
    date: string;
    count: number;
  }[];
  lead_funnel?: {
    stage: string;
    count: number;
  }[];
  roi_over_time?: {
    date: string;
    value: number;
  }[];
  ai_action_breakdown?: {
    type: string;
    count: number;
  }[];
  urgent_emails?: number;
}

export interface EmailPatterns {
  peak_hours: { hour: number; count: number }[];
  top_senders: { email: string; count: number }[];
  response_times: { avg_minutes: number; date: string }[];
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// Form Types
export interface CreateTaskData {
  title: string;
  description?: string;
  task_type: TaskType;
  priority: TaskPriority;
  due_date?: string;
  due_time?: string;
  message_id?: number;
  property_id?: number;
}

export interface CreateTransactionData {
  title: string;
  description?: string;
  transaction_type: TransactionType;
  contact_id: number;
  property_id?: number;
  estimated_value?: number;
  commission_percentage?: number;
  stage?: TransactionStage;
}

export interface CreateContactData {
  first_name: string;
  last_name?: string;
  email?: string;
  phone?: string;
  company?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  notes?: string;
  tags?: string[];
}

export interface CreatePropertyData {
  address: string;
  city?: string;
  state?: string;
  zip_code?: string;
  mls_id?: string;
  property_type?: string;
  list_price?: number;
  transaction_type?: string;
}

export interface CreateDraftData {
  communication_log_id: number;
  num_variants?: number;
  context?: Record<string, any>;
}

export interface UpdateDraftData {
  content?: string;
  feedback?: string;
}

