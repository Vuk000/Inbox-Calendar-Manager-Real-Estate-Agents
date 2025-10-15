/**
 * Task Creator Component
 * Phase 4.3: Quick task creation from emails
 */
import { useState } from 'react'
import { TaskPriority } from '../types'

interface TaskCreatorProps {
  emailId?: number
  suggestedTitle?: string
  suggestedDescription?: string
  suggestedPriority?: TaskPriority
  onCreateTask: (taskData: TaskFormData) => Promise<void>
  onCancel: () => void
}

interface TaskFormData {
  title: string
  description?: string
  priority: TaskPriority
  due_date?: string
  email_id?: number
}

export function TaskCreator({
  emailId,
  suggestedTitle = '',
  suggestedDescription = '',
  suggestedPriority = 'medium',
  onCreateTask,
  onCancel,
}: TaskCreatorProps) {
  const [title, setTitle] = useState(suggestedTitle)
  const [description, setDescription] = useState(suggestedDescription)
  const [priority, setPriority] = useState<TaskPriority>(suggestedPriority)
  const [dueDate, setDueDate] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!title.trim()) {
      alert('Please enter a task title')
      return
    }
    
    setIsSubmitting(true)
    
    try {
      await onCreateTask({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        due_date: dueDate || undefined,
        email_id: emailId,
      })
    } catch (error) {
      console.error('Failed to create task:', error)
      alert('Failed to create task. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Quick due date presets
  const setQuickDueDate = (days: number) => {
    const date = new Date()
    date.setDate(date.getDate() + days)
    setDueDate(date.toISOString().split('T')[0])
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      <h2 className="text-xl font-semibold mb-4">Create Task</h2>
      
      {emailId && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm">
          <span className="text-blue-700">
            ✉️ Creating task from email #{emailId}
          </span>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Task Title *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Schedule showing for 123 Main Street"
            required
            maxLength={200}
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Add details about this task..."
            rows={4}
          />
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Priority
          </label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setPriority('low')}
              className={`flex-1 px-4 py-2 rounded-md border ${
                priority === 'low'
                  ? 'bg-green-100 border-green-500 text-green-700'
                  : 'border-gray-300 hover:bg-gray-50'
              }`}
            >
              Low
            </button>
            <button
              type="button"
              onClick={() => setPriority('medium')}
              className={`flex-1 px-4 py-2 rounded-md border ${
                priority === 'medium'
                  ? 'bg-yellow-100 border-yellow-500 text-yellow-700'
                  : 'border-gray-300 hover:bg-gray-50'
              }`}
            >
              Medium
            </button>
            <button
              type="button"
              onClick={() => setPriority('high')}
              className={`flex-1 px-4 py-2 rounded-md border ${
                priority === 'high'
                  ? 'bg-red-100 border-red-500 text-red-700'
                  : 'border-gray-300 hover:bg-gray-50'
              }`}
            >
              High
            </button>
          </div>
        </div>

        {/* Due Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Due Date
          </label>
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          
          {/* Quick presets */}
          <div className="flex gap-2 mt-2">
            <button
              type="button"
              onClick={() => setQuickDueDate(1)}
              className="px-3 py-1 text-xs border border-gray-300 rounded hover:bg-gray-50"
            >
              Tomorrow
            </button>
            <button
              type="button"
              onClick={() => setQuickDueDate(3)}
              className="px-3 py-1 text-xs border border-gray-300 rounded hover:bg-gray-50"
            >
              In 3 days
            </button>
            <button
              type="button"
              onClick={() => setQuickDueDate(7)}
              className="px-3 py-1 text-xs border border-gray-300 rounded hover:bg-gray-50"
            >
              Next week
            </button>
            <button
              type="button"
              onClick={() => setDueDate('')}
              className="px-3 py-1 text-xs border border-gray-300 rounded hover:bg-gray-50"
            >
              No date
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            disabled={isSubmitting || !title.trim()}
          >
            {isSubmitting ? 'Creating...' : 'Create Task'}
          </button>
        </div>
      </form>

      {/* TODO Markers for Future Enhancements */}
      {/* TODO: Add smart scheduling - suggest optimal time slots */}
      {/* TODO: Integrate with Google Calendar for availability checking */}
      {/* TODO: Add task templates for common scenarios */}
      {/* TODO: Implement recurring task creation */}
      {/* TODO: Add attachments from email */}
      {/* TODO: Add task delegation (assign to team members) */}
    </div>
  )
}

