import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '../services/api'
import {
  EnvelopeIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  ClockIcon,
  BoltIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { format } from 'date-fns'

const colors = ['#2563eb', '#f59e0b', '#10b981', '#ef4444', '#9333ea']

export default function DashboardPage() {
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: analyticsService.getDashboard,
  })

  const chartData = useMemo(() => ({
    activity: dashboardData?.email_activity || [],
    funnels: dashboardData?.lead_funnel || [],
    actions: dashboardData?.ai_action_breakdown || [],
    roi: dashboardData?.roi_over_time || [],
  }), [dashboardData])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const stats = [
    {
      name: 'Emails Processed Today',
      value: dashboardData?.emails_processed_today || 0,
      icon: EnvelopeIcon,
      color: 'bg-primary-500',
      change: '+12%',
      changeType: 'increase'
    },
    {
      name: 'Time Saved This Week',
      value: `${dashboardData?.time_saved_hours || 0}h`,
      icon: ClockIcon,
      color: 'bg-success-500',
      change: '+8.2h',
      changeType: 'increase'
    },
    {
      name: 'AI Drafts Generated',
      value: dashboardData?.drafts_generated || 0,
      icon: DocumentTextIcon,
      color: 'bg-warning-500',
      change: '+23',
      changeType: 'increase'
    },
    {
      name: 'Tasks Completed',
      value: dashboardData?.tasks_completed || 0,
      icon: CheckCircleIcon,
      color: 'bg-purple-500',
      change: '89%',
      changeType: 'increase'
    },
  ]

  const urgentEmails = dashboardData?.urgent_emails || []
  const recentLeads = dashboardData?.recent_leads || []

  return (
    <div className="space-y-8">
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Welcome back! 👋</h1>
          <p className="mt-2 text-gray-600">Operational intelligence for your inbox, leads, and tasks.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="btn-primary flex items-center">
            <BoltIcon className="h-5 w-5 mr-2" /> Automations
          </button>
          <button className="btn-secondary flex items-center">
            <ChartBarIcon className="h-5 w-5 mr-2" /> Export Report
          </button>
        </div>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div className={`${stat.color} rounded-lg p-3`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <span className={`text-sm font-medium ${
                stat.changeType === 'increase' ? 'text-success-600' : 'text-danger-600'
              }`}>
                {stat.change}
              </span>
            </div>
            <div className="mt-4">
              <p className="text-sm text-gray-600">{stat.name}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
            </div>
          </div>
        ))}
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <Card title="Email Activity" description="Messages processed by AI over the last 14 days" className="xl:col-span-2">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData.activity}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" tickFormatter={(value) => format(new Date(value), 'MM/dd')} stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ color: '#1f2937' }} />
              <Line type="monotone" dataKey="emails" stroke="#2563eb" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="ai_actions" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
        <Card title="AI Action Breakdown" description="Usage per automation type">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie dataKey="value" data={chartData.actions} innerRadius={60} outerRadius={100} paddingAngle={4}>
                {chartData.actions?.map((_entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <Card title="Lead Funnel" description="Lead progression through your pipeline" className="xl:col-span-2">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chartData.funnels}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="stage" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip />
              <Bar dataKey="count" radius={[8, 8, 0, 0]} fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card title="ROI Over Time" description="Hours saved vs. subscription cost">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData.roi}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#9ca3af" tickFormatter={(value) => format(new Date(value), 'MM/dd')} />
              <YAxis stroke="#9ca3af" />
              <Tooltip />
              <Line type="monotone" dataKey="hours_saved" stroke="#10b981" strokeWidth={2} />
              <Line type="monotone" dataKey="value_generated" stroke="#f59e0b" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Urgent Emails" description="Messages that need immediate attention">
          {urgentEmails.length > 0 ? (
            <div className="space-y-3">
              {urgentEmails.slice(0, 5).map((email: any) => (
                <div
                  key={email.id}
                  className="p-4 border border-danger-200 bg-danger-50 rounded-lg hover:bg-danger-100 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {email.subject}
                      </p>
                      <p className="text-sm text-gray-600 truncate mt-1">
                        From: {email.sender}
                      </p>
                    </div>
                    <span className="ml-2 px-2 py-1 text-xs font-medium rounded-full bg-danger-200 text-danger-800">
                      {email.category}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">
              No urgent emails. You're all caught up! 🎉
            </p>
          )}
        </Card>
        <Card title="Recent Leads" description="High intent conversations in the last 7 days">
          {recentLeads.length > 0 ? (
            <div className="space-y-3">
              {recentLeads.slice(0, 5).map((lead: any) => (
                <div
                  key={lead.id}
                  className="p-4 border border-success-200 bg-success-50 rounded-lg hover:bg-success-100 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">
                        {lead.name}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {lead.email}
                      </p>
                    </div>
                    <div className="ml-2 text-right">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        lead.score >= 80
                          ? 'bg-danger-200 text-danger-800'
                          : lead.score >= 50
                          ? 'bg-warning-200 text-warning-800'
                          : 'bg-gray-200 text-gray-800'
                      }`}>
                        Score: {lead.score}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">
              No new leads yet. Keep an eye on your inbox! 👀
            </p>
          )}
        </Card>
      </section>

      <section className="bg-primary-50 border border-primary-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="btn-primary">Connect Email Account</button>
          <button className="btn-outline">Schedule a Showing</button>
          <button className="btn-secondary">View All Tasks</button>
        </div>
      </section>
    </div>
  )
}

function Card({ title, description, className, children }: { title: string; description: string; className?: string; children: React.ReactNode }) {
  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className || ''}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
      {children}
    </div>
  )
}

