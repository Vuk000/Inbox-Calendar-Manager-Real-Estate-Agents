"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { ChevronLeft, ChevronRight, Plus, Clock, MapPin, Users, Video, Loader2, AlertCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { taskService } from "@/lib/api"
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, isToday } from "date-fns"
import Link from "next/link"

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [view, setView] = useState<"month" | "week" | "day">("month")

  // Fetch tasks as calendar events
  const { data: tasks = [], isLoading, error } = useQuery({
    queryKey: ['tasks', 'calendar'],
    queryFn: async () => {
      const response = await taskService.listTasks({})
      return Array.isArray(response) ? response : []
    },
    refetchOnWindowFocus: true,
  })

  // Convert tasks to calendar events
  const events = tasks
    .filter((task: any) => task.due_date)
    .map((task: any) => ({
      id: task.id,
      title: task.title,
      time: task.due_time || "All Day",
      date: new Date(task.due_date).getDate(),
      fullDate: new Date(task.due_date),
      type: task.task_type || "general",
      priority: task.priority,
      status: task.status,
      color: getEventColor(task.task_type, task.priority),
    }))

  // Get upcoming events (next 7 days)
  const upcomingEvents = events
    .filter((event) => {
      const eventDate = event.fullDate
      const today = new Date()
      const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
      return eventDate >= today && eventDate <= weekFromNow
    })
    .sort((a, b) => a.fullDate.getTime() - b.fullDate.getTime())
    .slice(0, 5)

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate()
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay()

  const monthStart = startOfMonth(currentDate)
  const monthEnd = endOfMonth(currentDate)
  const monthDays = eachDayOfInterval({ start: monthStart, end: monthEnd })

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))
  }

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))
  }

  const getEventsForDay = (day: number) => {
    return events.filter((event) => {
      const eventDate = new Date(event.fullDate)
      return (
        eventDate.getDate() === day &&
        eventDate.getMonth() === currentDate.getMonth() &&
        eventDate.getFullYear() === currentDate.getFullYear()
      )
    })
  }

  function getEventColor(taskType: string, priority: string) {
    if (priority === "high") return "bg-red-500"
    if (priority === "medium") return "bg-yellow-500"
    if (taskType === "showing") return "bg-blue-500"
    if (taskType === "closing") return "bg-green-500"
    if (taskType === "inspection") return "bg-purple-500"
    return "bg-gray-500"
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-balance">Calendar</h1>
          <p className="text-muted-foreground mt-1">Manage your appointments and tasks</p>
        </div>
        <Button className="glow-border" asChild>
          <Link href="/dashboard/tasks">
            <Plus className="w-4 h-4 mr-2" />
            New Task
          </Link>
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Calendar View */}
        <Card className="glass-card lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <CardTitle>
                  {format(currentDate, "MMMM yyyy")}
                </CardTitle>
                <div className="flex gap-2">
                  <Button variant="outline" size="icon" onClick={previousMonth}>
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="icon" onClick={nextMonth}>
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setCurrentDate(new Date())}>
                    Today
                  </Button>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center py-12">
                <AlertCircle className="w-8 h-8 text-destructive mb-4" />
                <p className="text-destructive">Failed to load calendar events</p>
              </div>
            ) : (
              <>
                {/* Day headers */}
                <div className="grid grid-cols-7 gap-1 mb-2">
                  {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
                    <div key={day} className="text-center text-sm font-semibold text-muted-foreground p-2">
                      {day}
                    </div>
                  ))}
                </div>

                {/* Calendar grid */}
                <div className="grid grid-cols-7 gap-1">
                  {/* Empty cells for days before month starts */}
                  {Array.from({ length: firstDayOfMonth }).map((_, index) => (
                    <div key={`empty-${index}`} className="aspect-square" />
                  ))}

                  {/* Days of the month */}
                  {monthDays.map((day) => {
                    const dayEvents = getEventsForDay(day.getDate())
                    const isTodayDate = isToday(day)

                    return (
                      <div
                        key={day.toISOString()}
                        className={`aspect-square border border-border rounded-lg p-1 cursor-pointer hover:bg-accent transition-colors ${
                          isTodayDate ? "bg-primary/10 border-primary" : ""
                        }`}
                      >
                        <div className={`text-xs font-semibold mb-1 ${isTodayDate ? "text-primary" : ""}`}>
                          {day.getDate()}
                        </div>
                        <div className="space-y-0.5">
                          {dayEvents.slice(0, 3).map((event) => (
                            <div
                              key={event.id}
                              className={`${event.color} text-white text-xs px-1 py-0.5 rounded truncate`}
                              title={event.title}
                            >
                              {event.title}
                            </div>
                          ))}
                          {dayEvents.length > 3 && (
                            <div className="text-xs text-muted-foreground">+{dayEvents.length - 3} more</div>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Upcoming Events Sidebar */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Upcoming Events</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
              </div>
            ) : upcomingEvents.length === 0 ? (
              <div className="text-center py-8">
                <Clock className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">No upcoming events</p>
                <Button variant="outline" size="sm" className="mt-4" asChild>
                  <Link href="/dashboard/tasks">Create Task</Link>
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {upcomingEvents.map((event) => (
                  <div key={event.id} className="p-3 border border-border rounded-lg hover:bg-accent transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <p className="font-semibold text-sm">{event.title}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Clock className="w-3 h-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">
                            {format(event.fullDate, "MMM d")} • {event.time}
                          </span>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-xs capitalize">
                        {event.status}
                      </Badge>
                    </div>
                    <Badge
                      variant="secondary"
                      className="text-xs capitalize"
                      style={{ backgroundColor: event.color, color: "white" }}
                    >
                      {event.type.replace("_", " ")}
                    </Badge>
                  </div>
                ))}
                <Button variant="outline" className="w-full" asChild>
                  <Link href="/dashboard/tasks">View All Tasks</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
