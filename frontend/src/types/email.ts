/**
 * Email Domain Types
 * Types specific to email management features
 */

import { Priority, EmailCategory, EmailEntities, TriageResult } from './api'

export interface EmailFilters {
  priority?: Priority | 'all'
  category?: EmailCategory | 'all'
  is_read?: boolean
  is_starred?: boolean
  has_attachments?: boolean
  date_from?: string
  date_to?: string
  search_query?: string
}

export interface EmailSortOptions {
  field: 'received_at' | 'urgency_score' | 'sender_name' | 'subject'
  direction: 'asc' | 'desc'
}

export interface EmailThread {
  thread_id: string
  subject: string
  participants: string[]
  message_count: number
  latest_message_at: string
  messages: EmailMessage[]
}

export interface EmailMessage {
  id: number
  thread_id: string
  subject: string
  sender_email: string
  sender_name: string
  body: string
  received_at: string
  is_read: boolean
}

export interface EmailAttachment {
  id: string
  filename: string
  size: number
  mime_type: string
  url: string
}

export interface EmailAction {
  type: 'reply' | 'forward' | 'archive' | 'delete' | 'mark_read' | 'star' | 'create_task' | 'generate_draft'
  label: string
  icon: string
  handler: (emailId: number) => void | Promise<void>
}

export interface EmailStats {
  total: number
  unread: number
  high_priority: number
  pending_response: number
  with_tasks: number
}

export interface BulkEmailAction {
  action: 'mark_read' | 'mark_unread' | 'archive' | 'delete' | 'star' | 'unstar'
  email_ids: number[]
}

// Email compose/reply types
export interface EmailCompose {
  to: string[]
  cc?: string[]
  bcc?: string[]
  subject: string
  body: string
  attachments?: File[]
  in_reply_to?: number
  thread_id?: string
}

export interface EmailRecipient {
  email: string
  name?: string
  type: 'to' | 'cc' | 'bcc'
}

// Triage-specific types
export interface TriageFilters {
  min_urgency?: number
  max_urgency?: number
  categories?: EmailCategory[]
  has_deadline?: boolean
  requires_urgent_response?: boolean
  min_confidence?: number
}

export interface TriageSuggestion {
  action: string
  reason: string
  priority: number
}

