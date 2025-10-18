export type TransactionStage =
  | 'lead'
  | 'active'
  | 'pending'
  | 'under_contract'
  | 'closed_won'
  | 'closed_lost'
  | 'archived'

export type TransactionType = 'buyer' | 'seller' | 'both' | 'lease' | 'referral'

export interface Transaction {
  id: number
  user_id: number
  team_id: number | null
  title: string
  description: string | null
  transaction_type: TransactionType
  stage: TransactionStage
  pipeline_position: number
  contact_id: number
  property_id: number | null
  estimated_value: number | null
  commission_percentage: number | null
  estimated_commission: number | null
  actual_sale_price: number | null
  actual_commission: number | null
  lead_date: string | null
  contract_date: string | null
  closing_date: string | null
  closed_at: string | null
  probability: number
  is_shared: boolean
  public_timeline_uuid: string | null
  notes: string | null
  tags: string[]
  created_at: string
  updated_at: string | null
}

export interface TransactionCreate {
  title: string
  description?: string | null
  transaction_type: TransactionType
  contact_id: number
  property_id?: number | null
  estimated_value?: number | null
  commission_percentage?: number | null
  estimated_commission?: number | null
  checklist_template?: string
  lead_date?: string | null
  contract_date?: string | null
  closing_date?: string | null
  probability?: number
  notes?: string | null
  tags?: string[]
  is_shared?: boolean
}

export interface TransactionUpdate extends Partial<TransactionCreate> {
  stage?: TransactionStage
  actual_sale_price?: number | null
  actual_commission?: number | null
}

export interface TransactionListResponse {
  transactions: Transaction[]
  total: number
  skip: number
  limit: number
}

