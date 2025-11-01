"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus, Calendar, LayoutGrid, List, Loader2, Trash2, CheckCircle2 } from "lucide-react"
import { taskService } from "@/lib/api"
import toast from "react-hot-toast"
import { format } from "date-fns"

interface Task {
  id: number
  title: string
  description: string | null
  status: string
  priority: string
  due_date: string | null
  due_time: string | null
  task_type: string
  created_at: string
  updated_at: string
  is_completed: boolean
  completed_at: string | null
  message_id: number | null
  property_id: number | null
}

const statusColumns = [
  { id: "todo", label: "To Do", color: "from-gray-500 to-gray-600" },
  { id: "in_progress", label: "In Progress", color: "from-blue-500 to-cyan-500" },
  { id: "done", label: "Completed", color: "from-green-500 to-teal-500" },
  { id: "cancelled", label: "Cancelled", color: "from-gray-400 to-gray-500" },
]

export default function TasksPage() {
  const queryClient = useQueryClient()
  const [viewMode, setViewMode] = useState<"board" | "list">("board")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [selectedStatus, setSelectedStatus] = useState<string | undefined>(undefined)

  // Fetch tasks
  const { data: tasks = [], isLoading, error, refetch } = useQuery({
    queryKey: ['tasks', { status: selectedStatus }],
    queryFn: async () => {
      const params: any = {}
      if (selectedStatus) {
        params.status = selectedStatus
      }
      const response = await taskService.listTasks(params)
      return Array.isArray(response) ? response : []
    },
    refetchOnWindowFocus: true,
  })

  // Create task mutation
  const createTaskMutation = useMutation({
    mutationFn: async (data: any) => {
      return await taskService.createTask(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Task created successfully')
      setIsDialogOpen(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create task')
    },
  })

  // Update task mutation
  const updateTaskMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      return await taskService.updateTask(id, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Task updated successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update task')
    },
  })

  // Delete task mutation
  const deleteTaskMutation = useMutation({
    mutationFn: async (id: number) => {
      await taskService.deleteTask(id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('Task deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete task')
    },
  })

  const handleCreateTask = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = {
      title: formData.get('title') as string,
      description: formData.get('description') as string || null,
      task_type: formData.get('task_type') as string || 'general',
      priority: formData.get('priority') as string || 'medium',
      due_date: formData.get('due_date') as string || null,
      due_time: formData.get('due_time') as string || null,
    }
    createTaskMutation.mutate(data)
  }

  const handleStatusChange = (taskId: number, newStatus: string) => {
    updateTaskMutation.mutate({
      id: taskId,
      data: { status: newStatus },
    })
  }

  const handleDeleteTask = (taskId: number, title: string) => {
    if (confirm(`Are you sure you want to delete "${title}"?`)) {
      deleteTaskMutation.mutate(taskId)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "destructive"
      case "medium":
        return "secondary"
      case "low":
        return "outline"
      default:
        return "secondary"
    }
  }

  const getTasksByStatus = (status: string) => {
    return tasks.filter((task: Task) => {
      if (status === "done") {
        return task.status === "done" || task.is_completed
      }
      return task.status === status && !task.is_completed
    })
  }

  const formatDueDate = (dueDate: string | null) => {
    if (!dueDate) return "No due date"
    try {
      return format(new Date(dueDate), "MMM d, yyyy")
    } catch {
      return dueDate
    }
  }

  // Calculate stats
  const stats = {
    total: tasks.length,
    todo: getTasksByStatus("todo").length,
    inProgress: getTasksByStatus("in_progress").length,
    completed: getTasksByStatus("done").length,
    cancelled: getTasksByStatus("cancelled").length,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-balance">Tasks</h1>
          <p className="text-muted-foreground mt-1">Manage your tasks and deadlines</p>
        </div>
        <div className="flex gap-2">
          <div className="flex border rounded-lg bg-background/50">
            <Button
              variant={viewMode === "board" ? "default" : "ghost"}
              size="sm"
              onClick={() => setViewMode("board")}
              className="rounded-r-none"
            >
              <LayoutGrid className="w-4 h-4 mr-2" />
              Board
            </Button>
            <Button
              variant={viewMode === "list" ? "default" : "ghost"}
              size="sm"
              onClick={() => setViewMode("list")}
              className="rounded-l-none"
            >
              <List className="w-4 h-4 mr-2" />
              List
            </Button>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="glow-border">
                <Plus className="w-4 h-4 mr-2" />
                New Task
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Task</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateTask} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Title *</Label>
                  <Input id="title" name="title" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea id="description" name="description" rows={4} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="task_type">Task Type</Label>
                    <Select name="task_type" defaultValue="general">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="general">General</SelectItem>
                        <SelectItem value="showing">Showing</SelectItem>
                        <SelectItem value="inspection">Inspection</SelectItem>
                        <SelectItem value="closing">Closing</SelectItem>
                        <SelectItem value="follow_up">Follow-up</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="priority">Priority</Label>
                    <Select name="priority" defaultValue="medium">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="due_date">Due Date</Label>
                    <Input id="due_date" name="due_date" type="date" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="due_time">Due Time</Label>
                    <Input id="due_time" name="due_time" type="time" />
                  </div>
                </div>
                <div className="flex justify-end gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={createTaskMutation.isPending}>
                    {createTaskMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      "Create Task"
                    )}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-sm text-muted-foreground">Total Tasks</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{stats.todo}</div>
            <p className="text-sm text-muted-foreground">To Do</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{stats.inProgress}</div>
            <p className="text-sm text-muted-foreground">In Progress</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{stats.completed}</div>
            <p className="text-sm text-muted-foreground">Completed</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{stats.cancelled}</div>
            <p className="text-sm text-muted-foreground">Cancelled</p>
          </CardContent>
        </Card>
      </div>

      {/* Loading state */}
      {isLoading && (
        <Card className="glass-card">
          <CardContent className="p-12 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading tasks...</p>
          </CardContent>
        </Card>
      )}

      {/* Error state */}
      {error && (
        <Card className="glass-card border-destructive">
          <CardContent className="p-12 text-center">
            <p className="text-destructive mb-2">Failed to load tasks</p>
            <Button variant="outline" onClick={() => refetch()}>
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Tasks Board */}
      {!isLoading && !error && viewMode === "board" && (
        <div className="grid gap-4 lg:grid-cols-4">
          {statusColumns.map((column) => {
            const columnTasks = getTasksByStatus(column.id)
            return (
              <Card key={column.id} className="glass-card">
                <CardHeader className={`bg-gradient-to-r ${column.color} text-white rounded-t-lg p-4`}>
                  <CardTitle className="text-white flex items-center justify-between">
                    <span>{column.label}</span>
                    <Badge variant="secondary" className="bg-white/20 text-white">
                      {columnTasks.length}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4 space-y-3 min-h-[400px]">
                  {columnTasks.map((task: Task) => (
                    <Card key={task.id} className="glass-card bg-background/50 cursor-pointer hover:glow-border transition-all">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-semibold text-sm">{task.title}</h4>
                          <Badge variant={getPriorityColor(task.priority)} className="text-xs">
                            {task.priority}
                          </Badge>
                        </div>
                        {task.description && (
                          <p className="text-xs text-muted-foreground mb-2 line-clamp-2">{task.description}</p>
                        )}
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            <span>{formatDueDate(task.due_date)}</span>
                          </div>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6"
                              onClick={() => handleStatusChange(task.id, task.status === "done" ? "todo" : "done")}
                            >
                              <CheckCircle2 className="w-3 h-3" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6 text-destructive"
                              onClick={() => handleDeleteTask(task.id, task.title)}
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {columnTasks.length === 0 && (
                    <div className="text-center text-muted-foreground text-sm py-8">No tasks</div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Tasks List View */}
      {!isLoading && !error && viewMode === "list" && (
        <Card className="glass-card">
          <CardContent className="p-0">
            <div className="divide-y divide-border">
              {tasks.map((task: Task) => (
                <div key={task.id} className="p-4 hover:bg-accent/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <input
                        type="checkbox"
                        checked={task.is_completed || task.status === "done"}
                        onChange={() => handleStatusChange(task.id, task.is_completed ? "todo" : "done")}
                        className="w-4 h-4"
                      />
                      <div className="flex-1">
                        <h4 className={`font-semibold ${task.is_completed ? "line-through text-muted-foreground" : ""}`}>
                          {task.title}
                        </h4>
                        {task.description && (
                          <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
                        )}
                        <div className="flex items-center gap-4 mt-2">
                          <Badge variant={getPriorityColor(task.priority)} className="text-xs">
                            {task.priority}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {task.task_type}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            Due: {formatDueDate(task.due_date)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Select
                        value={task.status}
                        onValueChange={(value) => handleStatusChange(task.id, value)}
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="todo">To Do</SelectItem>
                          <SelectItem value="in_progress">In Progress</SelectItem>
                          <SelectItem value="done">Done</SelectItem>
                          <SelectItem value="cancelled">Cancelled</SelectItem>
                        </SelectContent>
                      </Select>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteTask(task.id, task.title)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {tasks.length === 0 && (
              <div className="p-12 text-center text-muted-foreground">
                <p>No tasks found. Create your first task to get started!</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
