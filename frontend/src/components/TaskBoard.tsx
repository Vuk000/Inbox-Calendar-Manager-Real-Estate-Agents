import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { taskService } from '../services/api'
import { 
  PlusIcon, 
  CalendarIcon,
  ClockIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'
import toast from 'react-hot-toast'

interface TaskBoardProps {
  propertyId?: number
}

export default function TaskBoard({ propertyId }: TaskBoardProps) {
  const queryClient = useQueryClient()

  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks', propertyId],
    queryFn: () => taskService.listTasks(propertyId ? { status: undefined, property_id: propertyId } as any : {}),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      taskService.updateTask(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Task updated')
    },
  })

  const columns = [
    { id: 'todo', title: 'To Do', color: 'border-gray-300' },
    { id: 'in_progress', title: 'In Progress', color: 'border-primary-300' },
    { id: 'done', title: 'Done', color: 'border-success-300' },
  ]

  const getTasksByStatus = (status: string) => {
    return tasks?.filter((task: any) => task.status === status) || []
  }

  const handleStatusChange = (taskId: number, newStatus: string) => {
    updateMutation.mutate({ id: taskId, status: newStatus })
  }

  const getPriorityColor = (priority: string) => {
    const colors = {
      high: 'bg-danger-100 text-danger-700 border-danger-200',
      medium: 'bg-warning-100 text-warning-700 border-warning-200',
      low: 'bg-gray-100 text-gray-700 border-gray-200'
    }
    return colors[priority as keyof typeof colors] || colors.low
  }

  const getTaskTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      showing: '🏠',
      inspection: '🔍',
      appraisal: '💰',
      signing: '✍️',
      deadline: '⏰',
      call: '📞',
      follow_up: '📧',
      general: '📋'
    }
    return icons[type] || '📋'
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Task Board</h2>
        <button
          className="btn-primary flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          New Task
        </button>
      </div>

      {/* Board */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {columns.map((column) => {
          const columnTasks = getTasksByStatus(column.id)
          
          return (
            <div key={column.id} className="flex flex-col">
              {/* Column Header */}
              <div className={`border-2 ${column.color} rounded-t-lg bg-gray-50 p-4`}>
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900">{column.title}</h3>
                  <span className="bg-white px-2 py-1 rounded-full text-sm font-medium text-gray-700">
                    {columnTasks.length}
                  </span>
                </div>
              </div>

              {/* Column Content */}
              <div className="border-2 border-t-0 border-gray-200 rounded-b-lg p-4 bg-white min-h-[500px] space-y-3">
                {columnTasks.length > 0 ? (
                  columnTasks.map((task: any) => (
                    <div
                      key={task.id}
                      className="bg-white border-2 border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-move"
                      draggable
                    >
                      {/* Task Header */}
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="text-2xl">{getTaskTypeIcon(task.task_type)}</span>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                          </span>
                        </div>
                        
                        {/* Status dropdown */}
                        <select
                          value={task.status}
                          onChange={(e) => handleStatusChange(task.id, e.target.value)}
                          className="text-xs border border-gray-300 rounded px-2 py-1"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <option value="todo">To Do</option>
                          <option value="in_progress">In Progress</option>
                          <option value="done">Done</option>
                          <option value="cancelled">Cancelled</option>
                        </select>
                      </div>

                      {/* Task Title */}
                      <h4 className="font-semibold text-gray-900 mb-2">
                        {task.title}
                      </h4>

                      {/* Task Description */}
                      {task.description && (
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                          {task.description}
                        </p>
                      )}

                      {/* Due Date */}
                      {task.due_date && (
                        <div className="flex items-center text-sm text-gray-600 mb-2">
                          <CalendarIcon className="h-4 w-4 mr-1" />
                          <span>
                            {new Date(task.due_date).toLocaleDateString()}
                            {task.due_time && ` at ${task.due_time}`}
                          </span>
                        </div>
                      )}

                      {/* Overdue indicator */}
                      {task.due_date && 
                       new Date(task.due_date) < new Date() && 
                       !task.is_completed && (
                        <div className="flex items-center text-sm text-danger-600 font-medium">
                          <ExclamationCircleIcon className="h-4 w-4 mr-1" />
                          Overdue by {formatDistanceToNow(new Date(task.due_date))}
                        </div>
                      )}

                      {/* Completed */}
                      {task.is_completed && task.completed_at && (
                        <div className="flex items-center text-sm text-success-600 mt-2">
                          <ClockIcon className="h-4 w-4 mr-1" />
                          Completed {formatDistanceToNow(new Date(task.completed_at), { addSuffix: true })}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    <p className="text-sm">No tasks</p>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Stats */}
      <div className="bg-gray-50 rounded-lg p-4 grid grid-cols-2 md:grid-cols-5 gap-4">
        <div>
          <p className="text-sm text-gray-600">Total</p>
          <p className="text-2xl font-bold text-gray-900">{tasks?.length || 0}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">To Do</p>
          <p className="text-2xl font-bold text-gray-700">
            {getTasksByStatus('todo').length}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">In Progress</p>
          <p className="text-2xl font-bold text-primary-600">
            {getTasksByStatus('in_progress').length}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Done</p>
          <p className="text-2xl font-bold text-success-600">
            {getTasksByStatus('done').length}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Overdue</p>
          <p className="text-2xl font-bold text-danger-600">
            {tasks?.filter((t: any) => 
              t.due_date && 
              new Date(t.due_date) < new Date() && 
              !t.is_completed
            ).length || 0}
          </p>
        </div>
      </div>
    </div>
  )
}

