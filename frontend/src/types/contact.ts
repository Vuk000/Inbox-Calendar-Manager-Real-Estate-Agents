export interface Contact {
  id: number
  user_id: number
  team_id: number | null
  first_name: string
  last_name: string | null
  company: string | null
  job_title: string | null
  email: string | null
  phone: string | null
  secondary_phone: string | null
  address_line1: string | null
  address_line2: string | null
  city: string | null
  state: string | null
  zip_code: string | null
  country: string
  contact_type: string | null
  contact_status: string
  lead_source: string | null
  relationship_score: number
  last_contact_date: string | null
  contact_frequency: number
  ai_insights: {
    summary?: string
    suggested_actions?: string[]
    communication_pattern?: string
    sentiment_trend?: string
  }
  preferred_contact_method: string | null
  tags: string[]
  custom_fields: Record<string, any>
  linkedin_url: string | null
  facebook_url: string | null
  twitter_handle: string | null
  notes: string | null
  is_shared_with_team: boolean
  created_at: string
  updated_at: string | null
}

export interface ContactCreate {
  first_name: string
  last_name?: string | null
  company?: string | null
  job_title?: string | null
  email?: string | null
  phone?: string | null
  secondary_phone?: string | null
  address_line1?: string | null
  address_line2?: string | null
  city?: string | null
  state?: string | null
  zip_code?: string | null
  country?: string
  contact_type?: string | null
  lead_source?: string | null
  preferred_contact_method?: string | null
  tags?: string[]
  custom_fields?: Record<string, any>
  linkedin_url?: string | null
  facebook_url?: string | null
  twitter_handle?: string | null
  notes?: string | null
}

export interface ContactUpdate extends Partial<ContactCreate> {
  contact_status?: string
}

export interface ContactListResponse {
  contacts: Contact[]
  total: number
  skip: number
  limit: number
}

export interface ContactImportResult {
  success: boolean
  imported_count: number
  skipped_count: number
  errors: string[]
}

