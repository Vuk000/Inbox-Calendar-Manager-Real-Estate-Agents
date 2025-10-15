/**
 * Task Domain Types
 * Types specific to task management features
 */

import { TaskStatus, TaskPriority } from './api'

export interface TaskFilters {
  status?: TaskStatus | 'all'
  priority?: TaskPriority | 'all'
  assigned_to?: number
  created_by?: number
  has_due_date?: boolean
  is_overdue?: boolean
  date_from?: string
  date_to?: string
}

export interface TaskSortOptions {
  field: 'created_at' | 'due_date' | 'priority' | 'title'
  direction: 'asc' | 'desc'
}

export interface TaskBoard {
  pending: TaskColumn
  in_progress: TaskColumn
  completed: TaskColumn
}

export interface TaskColumn {
  status: TaskStatus
  tasks: TaskCard[]
  count: number
}

export interface TaskCard {
  id: number
  title: string
  priority: TaskPriority
  due_date?: string
  is_overdue: boolean
  days_until_due?: number
  has_email: boolean
  tags: string[]
}

export interface TaskDetails {
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
  comments: TaskComment[]
  history: TaskHistory[]
  attachments: TaskAttachment[]
}

export interface TaskComment {
  id: number
  task_id: number
  user_id: number
  user_name: string
  comment: string
  created_at: string
}

export interface TaskHistory {
  id: number
  task_id: number
  user_id: number
  user_name: string
  action: string
  old_value?: string
  new_value?: string
  created_at: string
}

export interface TaskAttachment {
  id: number
  filename: string
  size: number
  url: string
  uploaded_at: string
}

export interface TaskStats {
  total: number
  pending: number
  in_progress: number
  completed: number
  overdue: number
  due_today: number
  due_this_week: number
  completion_rate: number
}

export interface TaskReminder {
  task_id: number
  remind_at: string
  method: 'email' | 'push' | 'sms'
  message?: string
}

export interface TaskTemplate {
  id: string
  name: string
  title_template: string
  description_template: string
  default_priority: TaskPriority
  default_due_days: number
  category: string
}

export interface QuickTask {
  title: string
  priority?: TaskPriority
  due_date?: string
}

export interface TaskBulkAction {
  action: 'update_status' | 'update_priority' | 'delete' | 'assign'
  task_ids: number[]
  new_status?: TaskStatus
  new_priority?: TaskPriority
  assign_to?: number
}

export interface TaskFromEmail {
  email_id: number
  suggested_title: string
  suggested_description: string
  suggested_due_date?: string
  suggested_priority: TaskPriority
  extracted_actions: string[]
}

