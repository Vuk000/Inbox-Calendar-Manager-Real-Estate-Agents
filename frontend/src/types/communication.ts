export type CommunicationType =
  | 'email'
  | 'sms'
  | 'whatsapp'
  | 'phone_call'
  | 'meeting'
  | 'note'
  | 'twitter_dm'
  | 'facebook_messenger'

export type CommunicationDirection = 'inbound' | 'outbound' | 'internal'

export interface CommunicationLog {
  id: number
  contact_id: number
  communication_type: CommunicationType
  direction: CommunicationDirection
  subject: string | null
  summary: string | null
  from_address: string | null
  to_address: string | null
  sentiment_score: number | null
  urgency_score: number | null
  occurred_at: string
}

export interface CommunicationStats {
  total_count: number
  by_type: Record<string, number>
  by_direction: Record<string, number>
  avg_sentiment: number | null
  last_contact: string | null
  frequency_per_month: number
}

export interface ContactTimeline {
  contact_id: number
  communications: CommunicationLog[]
}

