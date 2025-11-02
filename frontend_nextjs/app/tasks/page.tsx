'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { HolographicCard } from '@/components/cyberpunk/HolographicCard';
import { ScrollReveal } from '@/components/cyberpunk/ScrollReveal';
import { NeonText } from '@/components/cyberpunk/NeonText';
import { NeonButton } from '@/components/cyberpunk/NeonButton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { taskAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { Plus, CheckCircle2, Clock, AlertCircle, Trash2, Edit, Filter } from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { Dialog } from '@/components/ui/drawer';
import { toast } from 'react-hot-toast';
import { Select } from '@/components/ui/select';
import { Textarea } from '@/components/ui/input';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  assigned_to?: string;
  created_at: string;
}

interface SortableTaskProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (id: number) => void;
}

function SortableTask({ task, onEdit, onDelete }: SortableTaskProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const priorityColors = {
    low: 'bg-green-500/20 text-green-400 border-green-500/50',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    high: 'bg-red-500/20 text-red-400 border-red-500/50',
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <Card className="p-4 cursor-move hover:border-neon-cyan transition-colors">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-white flex-1">{task.title}</h3>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onEdit(task);
              }}
            >
              <Edit className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                if (confirm('Delete this task?')) {
                  onDelete(task.id);
                }
              }}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
        {task.description && (
          <p className="text-sm text-gray-400 mb-2 line-clamp-2">{task.description}</p>
        )}
        <div className="flex items-center justify-between">
          <Badge className={priorityColors[task.priority]}>
            {task.priority}
          </Badge>
          {task.due_date && (
            <span className="text-xs text-gray-500">
              Due: {new Date(task.due_date).toLocaleDateString()}
            </span>
          )}
        </div>
      </Card>
    </div>
  );
}

export default function TasksPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPriority, setFilterPriority] = useState<string>('all');

  const { data: tasks, isLoading, refetch } = useAPI(
    ['tasks', filterPriority],
    () => taskAPI.listTasks({ priority: filterPriority !== 'all' ? filterPriority : undefined }),
    { enabled: isAuthenticated }
  );

  const createTaskMutation = useAPIMutation(
    (task: Partial<Task>) => taskAPI.createTask(task),
    {
      onSuccess: () => {
        toast.success('Task created');
        setIsCreating(false);
        refetch();
      },
    }
  );

  const updateTaskMutation = useAPIMutation(
    ({ id, updates }: { id: number; updates: Partial<Task> }) => taskAPI.updateTask(id, updates),
    {
      onSuccess: () => {
        toast.success('Task updated');
        setSelectedTask(null);
        refetch();
      },
    }
  );

  const deleteTaskMutation = useAPIMutation(
    (id: number) => taskAPI.deleteTask?.(id) || Promise.resolve(),
    {
      onSuccess: () => {
        toast.success('Task deleted');
        refetch();
      },
    }
  );

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const columns = ['todo', 'in_progress', 'done'] as const;
  const columnLabels = {
    todo: 'To Do',
    in_progress: 'In Progress',
    done: 'Done',
  };
  const columnIcons = {
    todo: Clock,
    in_progress: AlertCircle,
    done: CheckCircle2,
  };

  const tasksByStatus = useMemo(() => {
    const taskList = tasks || [];
    return columns.reduce((acc, status) => {
      acc[status] = taskList.filter((task: Task) => {
        const matchesStatus = task.status === status;
        const matchesSearch = !searchQuery || 
          task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          task.description?.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;
        return matchesStatus && matchesSearch && matchesPriority;
      });
      return acc;
    }, {} as Record<string, Task[]>);
  }, [tasks, searchQuery, filterPriority]);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id as number;
    const activeTask = [...(tasks || [])].find((t: Task) => t.id === activeId);
    if (!activeTask) return;

    const newStatus = over.id as string;
    if (newStatus && columns.includes(newStatus as any)) {
      updateTaskMutation.mutate({
        id: activeId,
        updates: { status: newStatus as Task['status'] },
      });
    }
  };

  const handleCreateTask = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    createTaskMutation.mutate({
      title: formData.get('title') as string,
      description: formData.get('description') as string,
      priority: (formData.get('priority') as Task['priority']) || 'medium',
      due_date: formData.get('due_date') ? (formData.get('due_date') as string) : undefined,
      status: 'todo',
    });
  };

  const handleUpdateTask = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedTask) return;
    const formData = new FormData(e.currentTarget);
    updateTaskMutation.mutate({
      id: selectedTask.id,
      updates: {
        title: formData.get('title') as string,
        description: formData.get('description') as string,
        priority: (formData.get('priority') as Task['priority']) || 'medium',
        due_date: formData.get('due_date') ? (formData.get('due_date') as string) : undefined,
        status: (formData.get('status') as Task['status']) || 'todo',
      },
    });
  };

  if (!isAuthenticated) {
    router.push('/');
    return null;
  }

  return (
    <div className="flex min-h-screen bg-dark-bg">
      <Sidebar />
      <div className="flex-1 md:ml-64 p-4 md:p-8">
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          <ScrollReveal>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-4xl font-orbitron font-bold mb-2">
                  <NeonText color="pink">Tasks</NeonText>
                </h1>
                <p className="text-gray-400">Kanban board for task management</p>
              </div>
              <NeonButton onClick={() => setIsCreating(true)} glowColor="pink">
                <Plus className="w-4 h-4 mr-2" />
                New Task
              </NeonButton>
            </div>
          </ScrollReveal>

          {/* Search and Filters */}
          <Card className="p-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search tasks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select
                options={[
                  { value: 'all', label: 'All Priorities' },
                  { value: 'high', label: 'High' },
                  { value: 'medium', label: 'Medium' },
                  { value: 'low', label: 'Low' },
                ]}
                value={filterPriority}
                onChange={(value) => setFilterPriority(value)}
                placeholder="Filter by priority"
                className="w-48"
              />
            </div>
          </Card>

          {/* Kanban Board */}
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {columns.map((status) => {
                const Icon = columnIcons[status];
                const columnTasks = tasksByStatus[status] || [];

                return (
                  <div key={status} className="flex flex-col">
                    <Card className="p-4 mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Icon className="w-5 h-5 text-neon-cyan" />
                        <h2 className="text-lg font-orbitron text-neon-cyan">
                          {columnLabels[status]}
                        </h2>
                        <Badge variant="info">{columnTasks.length}</Badge>
                      </div>
                    </Card>
                    <SortableContext
                      items={columnTasks.map((t: Task) => t.id)}
                      strategy={verticalListSortingStrategy}
                    >
                      <div className="space-y-3 min-h-[400px]">
                        {columnTasks.map((task: Task) => (
                          <SortableTask
                            key={task.id}
                            task={task}
                            onEdit={setSelectedTask}
                            onDelete={(id) => deleteTaskMutation.mutate(id)}
                          />
                        ))}
                      </div>
                    </SortableContext>
                  </div>
                );
              })}
            </div>
          </DndContext>

          {/* Create Task Dialog */}
          <Dialog
            isOpen={isCreating}
            onClose={() => setIsCreating(false)}
            title="Create New Task"
            size="md"
          >
            <form onSubmit={handleCreateTask} className="space-y-4">
              <Input
                name="title"
                label="Title"
                placeholder="Task title"
                required
              />
              <Textarea
                name="description"
                label="Description"
                placeholder="Task description"
              />
              <Select
                name="priority"
                label="Priority"
                options={[
                  { value: 'low', label: 'Low' },
                  { value: 'medium', label: 'Medium' },
                  { value: 'high', label: 'High' },
                ]}
                value="medium"
                onChange={() => {}}
              />
              <Input
                name="due_date"
                label="Due Date"
                type="date"
              />
              <div className="flex gap-2 justify-end">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setIsCreating(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary">
                  Create Task
                </Button>
              </div>
            </form>
          </Dialog>

          {/* Edit Task Dialog */}
          <Dialog
            isOpen={!!selectedTask}
            onClose={() => setSelectedTask(null)}
            title="Edit Task"
            size="md"
          >
            {selectedTask && (
              <form onSubmit={handleUpdateTask} className="space-y-4">
                <Input
                  name="title"
                  label="Title"
                  defaultValue={selectedTask.title}
                  required
                />
                <Textarea
                  name="description"
                  label="Description"
                  defaultValue={selectedTask.description || ''}
                />
                <Select
                  name="priority"
                  label="Priority"
                  options={[
                    { value: 'low', label: 'Low' },
                    { value: 'medium', label: 'Medium' },
                    { value: 'high', label: 'High' },
                  ]}
                  value={selectedTask.priority}
                  onChange={() => {}}
                />
                <Select
                  name="status"
                  label="Status"
                  options={[
                    { value: 'todo', label: 'To Do' },
                    { value: 'in_progress', label: 'In Progress' },
                    { value: 'done', label: 'Done' },
                  ]}
                  value={selectedTask.status}
                  onChange={() => {}}
                />
                <Input
                  name="due_date"
                  label="Due Date"
                  type="date"
                  defaultValue={selectedTask.due_date ? new Date(selectedTask.due_date).toISOString().split('T')[0] : ''}
                />
                <div className="flex gap-2 justify-end">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setSelectedTask(null)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" variant="primary">
                    Save Changes
                  </Button>
                </div>
              </form>
            )}
          </Dialog>
        </motion.div>
      </div>
    </div>
  );
}

