/**
 * Draft Domain Types
 * Types specific to email draft generation and management
 */

import { DraftVariant } from './api'

export interface DraftGenerationOptions {
  email_id: number
  num_variants: number
  tone?: 'warm' | 'professional' | 'concise'
  include_style_examples: boolean
  style_examples?: string[]
  context?: DraftContext
}

export interface DraftContext {
  crm_data?: Record<string, any>
  property_data?: PropertyContext
  market_data?: MarketContext
  previous_interactions?: string[]
}

export interface PropertyContext {
  address: string
  price: number
  bedrooms: number
  bathrooms: number
  features?: string[]
  listing_url?: string
}

export interface MarketContext {
  average_price?: number
  days_on_market?: number
  comparable_sales?: number
  market_trend?: 'up' | 'down' | 'stable'
}

export interface DraftEditState {
  draft_id: number
  variant_number: number
  original_content: string
  edited_content: string
  is_modified: boolean
  word_count: number
  char_count: number
}

export interface DraftComparison {
  original: string
  modified: string
  additions: TextDiff[]
  deletions: TextDiff[]
  modifications: TextDiff[]
}

export interface TextDiff {
  start: number
  end: number
  text: string
  type: 'add' | 'delete' | 'modify'
}

export interface DraftFeedback {
  draft_id: number
  variant_number: number
  feedback_type: 'improve' | 'regenerate' | 'tone_change'
  feedback_text: string
  desired_tone?: 'warm' | 'professional' | 'concise'
}

export interface DraftTemplate {
  id: string
  name: string
  description: string
  template_text: string
  variables: string[]
  category: string
  use_count: number
}

export interface DraftStats {
  total_generated: number
  total_approved: number
  total_sent: number
  avg_confidence_score: number
  avg_word_count: number
  approval_rate: number
  most_used_tone?: 'warm' | 'professional' | 'concise'
}

export interface DraftVariantComparison {
  variant_1: DraftVariant
  variant_2: DraftVariant
  differences: {
    word_count_diff: number
    tone_diff: string
    cta_comparison: string
    confidence_diff: number
  }
}

export interface DraftApprovalOptions {
  send_immediately: boolean
  schedule_send?: string
  add_to_queue: boolean
  notify_on_send: boolean
  track_opens: boolean
}

export interface DraftQueue {
  id: number
  draft_id: number
  scheduled_for?: string
  status: 'queued' | 'sending' | 'sent' | 'failed'
  retry_count: number
  created_at: string
}

