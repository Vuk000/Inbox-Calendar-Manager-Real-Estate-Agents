"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, Mail, Calendar, TrendingUp, Users, CheckCircle2, Clock, Loader2, Phone } from "lucide-react"
import Link from "next/link"
import { useAuthStore } from "@/lib/stores/authStore"
import { contactsService, emailService, taskService, communicationsService } from "@/lib/api"
import toast from "react-hot-toast"
import { formatDistanceToNow } from "date-fns"
import { useQuery } from "@tanstack/react-query"

interface DashboardStats {
  activeContacts: number
  unreadEmails: number
  urgentEmails: number
  tasksToday: number
  tasksCompleted: number
  upcomingMeetings: number
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  
  // Fetch dashboard data with React Query
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      try {
        const [emailStatsRes, contactsRes, tasksRes, commsRes] = await Promise.all([
          emailService.getEmailStats().catch(() => ({ total: 0, unread: 0, urgent: 0 })),
          contactsService.listContacts({ limit: 100 }).catch(() => ({ contacts: [], total: 0 })),
          taskService.listTasks().catch(() => []),
          communicationsService.listCommunications({ limit: 4 }).catch(() => []),
        ])

        // Calculate stats
        const today = new Date().toISOString().split('T')[0]
        const todayTasks = Array.isArray(tasksRes) ? tasksRes.filter((t: any) => 
          t.due_date?.startsWith(today)
        ) : []
        const completedToday = todayTasks.filter((t: any) => t.status === 'done' || t.is_completed)

        // Get priority contacts
        const highPriorityContacts = (contactsRes.contacts || [])
          .filter((c: any) => 
            c.contact_status === 'hot_lead' || 
            c.contact_status === 'active' ||
            c.relationship_score > 0.7
          )
          .slice(0, 4)

        return {
          stats: {
            activeContacts: contactsRes.total || contactsRes.contacts?.length || 0,
            unreadEmails: emailStatsRes.unread || 0,
            urgentEmails: emailStatsRes.urgent || 0,
            tasksToday: todayTasks.length,
            tasksCompleted: completedToday.length,
            upcomingMeetings: 0,
          },
          priorityContacts: highPriorityContacts,
          recentActivity: Array.isArray(commsRes) ? commsRes : [],
        }
      } catch (error) {
        console.error('Error loading dashboard:', error)
        toast.error('Failed to load dashboard data')
        return {
          stats: {
            activeContacts: 0,
            unreadEmails: 0,
            urgentEmails: 0,
            tasksToday: 0,
            tasksCompleted: 0,
            upcomingMeetings: 0,
          },
          priorityContacts: [],
          recentActivity: [],
        }
      }
    },
    refetchOnWindowFocus: true,
  })

  const stats = dashboardData?.stats || {
    activeContacts: 0,
    unreadEmails: 0,
    urgentEmails: 0,
    tasksToday: 0,
    tasksCompleted: 0,
    upcomingMeetings: 0,
  }

  const priorityContacts = dashboardData?.priorityContacts || []
  const recentActivity = dashboardData?.recentActivity || []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <div>
        <h1 className="text-3xl font-bold text-balance">Welcome back, {user?.full_name?.split(' ')[0] || 'John'}</h1>
        <p className="text-muted-foreground mt-1">Here's what's happening with your business today</p>
      </div>

      {/* Stats grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Contacts</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeContacts}</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <TrendingUp className="h-3 w-3 text-primary" />
              <Link href="/dashboard/contacts" className="text-primary hover:underline">
                View all contacts
              </Link>
            </p>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unread Messages</CardTitle>
            <Mail className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.unreadEmails}</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              {stats.urgentEmails > 0 ? (
                <>
                  <span className="text-destructive">{stats.urgentEmails} urgent</span> require attention
                </>
              ) : (
                <Link href="/dashboard/inbox" className="text-primary hover:underline">
                  View inbox
                </Link>
              )}
            </p>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tasks Due Today</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.tasksToday}</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              {stats.tasksCompleted > 0 ? (
                <>
                  <span className="text-primary">{stats.tasksCompleted} completed</span> so far
                </>
              ) : (
                <Link href="/dashboard/tasks" className="text-primary hover:underline">
                  View all tasks
                </Link>
              )}
            </p>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Upcoming Meetings</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.upcomingMeetings}</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <Clock className="h-3 w-3" />
              {stats.upcomingMeetings > 0 ? (
                "Next in 45 minutes"
              ) : (
                <Link href="/dashboard/calendar" className="text-primary hover:underline">
                  View calendar
                </Link>
              )}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent activity */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest interactions and updates</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentActivity.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                No recent activity to display
              </p>
            ) : (
              recentActivity.map((activity: any, i: number) => {
                const activityType = activity.communication_type || 'email'
                const activityTime = activity.created_at || activity.occurred_at
                  ? formatDistanceToNow(new Date(activity.created_at || activity.occurred_at), { addSuffix: true })
                  : 'recently'
                const contactName = activity.contact_name || activity.from_address?.split('@')[0] || 'Unknown'

                return (
                  <div key={activity.id || i} className="flex items-center gap-4">
                    <Avatar className="h-9 w-9">
                      <AvatarFallback>
                        {contactName.split(" ").map((n: string) => n[0]).join("").toUpperCase() || "?"}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {contactName}{" "}
                        <span className="text-muted-foreground font-normal">
                          {activityType === 'email' && 'sent you an email'}
                          {activityType === 'call' && 'called you'}
                          {activityType === 'meeting' && 'had a meeting'}
                          {activityType === 'note' && 'added a note'}
                        </span>
                      </p>
                      <p className="text-xs text-muted-foreground">{activityTime}</p>
                    </div>
                    {activityType === "email" && <Mail className="h-4 w-4 text-muted-foreground" />}
                    {activityType === "meeting" && <Calendar className="h-4 w-4 text-muted-foreground" />}
                    {activityType === "call" && <Phone className="h-4 w-4 text-muted-foreground" />}
                    {activityType === "note" && <Users className="h-4 w-4 text-muted-foreground" />}
                  </div>
                )
              })
            )}
          </CardContent>
        </Card>

        {/* Priority contacts */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Priority Contacts</CardTitle>
            <CardDescription>Contacts that need your attention</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {priorityContacts.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">
                No priority contacts at the moment
              </p>
            ) : (
              priorityContacts.map((contact: any) => {
                const fullName = `${contact.first_name || ''} ${contact.last_name || ''}`.trim() || 'Unknown'
                const initials = fullName.split(" ").map((n) => n[0]).join("").toUpperCase()
                const lastContactTime = contact.last_contact_date
                  ? formatDistanceToNow(new Date(contact.last_contact_date), { addSuffix: true })
                  : 'No recent contact'
                const statusDisplay = contact.contact_status?.replace(/_/g, ' ') || 'Contact'

                return (
                  <div key={contact.id} className="flex items-center gap-4">
                    <Avatar className="h-9 w-9">
                      <AvatarFallback>{initials}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium leading-none">{fullName}</p>
                        <Badge
                          variant={contact.contact_status === "hot_lead" ? "destructive" : "secondary"}
                          className="text-xs capitalize"
                        >
                          {statusDisplay}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">Last contact: {lastContactTime}</p>
                    </div>
                    <Button variant="ghost" size="icon" asChild>
                      <Link href={`/dashboard/contacts/${contact.id}`}>
                        <ArrowUpRight className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                )
              })
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks to help you stay productive</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Button variant="outline" className="justify-start gap-2 h-auto py-3 bg-transparent" asChild>
              <Link href="/dashboard/contacts">
                <Users className="h-4 w-4" />
                Add New Contact
              </Link>
            </Button>
            <Button variant="outline" className="justify-start gap-2 h-auto py-3 bg-transparent" asChild>
              <Link href="/dashboard/inbox">
                <Mail className="h-4 w-4" />
                Compose Email
              </Link>
            </Button>
            <Button variant="outline" className="justify-start gap-2 h-auto py-3 bg-transparent" asChild>
              <Link href="/dashboard/calendar">
                <Calendar className="h-4 w-4" />
                Schedule Meeting
              </Link>
            </Button>
            <Button variant="outline" className="justify-start gap-2 h-auto py-3 bg-transparent" asChild>
              <Link href="/dashboard/tasks">
                <CheckCircle2 className="h-4 w-4" />
                Create Task
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
