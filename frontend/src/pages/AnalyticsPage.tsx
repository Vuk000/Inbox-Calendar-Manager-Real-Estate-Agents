import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '../services/api'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  LineChart,
  Line
} from 'recharts'
import { ClockIcon, CurrencyDollarIcon, ArrowTrendingUpIcon, ChartBarIcon } from '@heroicons/react/24/outline'
import { format } from 'date-fns'

export default function AnalyticsPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics', 'reports'],
    queryFn: () => analyticsService.getReports(),
  })

  const charts = useMemo(() => ({
    roi: analytics?.roi_timeseries || [],
    emailPatterns: analytics?.email_patterns || [],
    aiSavings: analytics?.ai_value_curve || [],
    channelBreakdown: analytics?.channel_breakdown || [],
  }), [analytics])

  const cards = [
    {
      title: 'Hours Saved (30d)',
      value: analytics?.email_metrics?.time_saved_hours || 0,
      icon: ClockIcon,
      gradient: 'from-primary-500 to-primary-600',
      footer: 'AI triage & draft automation'
    },
    {
      title: 'Value Generated',
      value: `$${(analytics?.email_metrics?.time_saved_hours || 0) * 50}`,
      icon: CurrencyDollarIcon,
      gradient: 'from-success-500 to-success-600',
      footer: 'Assuming $50/hr agent rate'
    },
    {
      title: 'Average ROI',
      value: `${analytics?.email_metrics?.roi_percentage || 0}%`,
      icon: ArrowTrendingUpIcon,
      gradient: 'from-warning-500 to-warning-600',
      footer: 'Compared with subscription cost'
    },
    {
      title: 'Emails Processed',
      value: analytics?.email_metrics?.processed || 0,
      icon: ChartBarIcon,
      gradient: 'from-purple-500 to-purple-600',
      footer: 'AI analyzed in the last 30 days'
    }
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">Analytics & Insights</h1>
        <p className="text-gray-600 mt-2">Quantify AI impact across your inbox, leads, and operations.</p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {cards.map((card) => (
          <div key={card.title} className={`rounded-lg p-6 text-white shadow-lg bg-gradient-to-br ${card.gradient}`}>
            <div className="flex items-center justify-between">
              <card.icon className="h-8 w-8 opacity-80" />
              <span className="text-sm uppercase tracking-wide opacity-80">30 days</span>
            </div>
            <div className="mt-4">
              <p className="text-sm opacity-80">{card.title}</p>
              <p className="text-3xl font-bold mt-1">{card.value}</p>
            </div>
            <p className="text-xs opacity-70 mt-4">{card.footer}</p>
          </div>
        ))}
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <AnalyticsCard title="ROI over time" subtitle="Hours saved vs. subscription spend in the last 12 weeks">
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={charts.roi}>
              <defs>
                <linearGradient id="roiGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#9ca3af" tickFormatter={(value) => format(new Date(value), 'MM/dd')} />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ color: '#1f2937' }} />
              <Area type="monotone" dataKey="hours_saved" stroke="#2563eb" fill="url(#roiGradient)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </AnalyticsCard>
        <AnalyticsCard title="Channel performance" subtitle="Messages processed per channel">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={charts.channelBreakdown}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="channel" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip />
              <Bar dataKey="messages" radius={[6, 6, 0, 0]} fill="#9333ea" />
            </BarChart>
          </ResponsiveContainer>
        </AnalyticsCard>
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <AnalyticsCard title="Email patterns" subtitle="Average response times by hour of day">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={charts.emailPatterns}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="hour" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip />
              <Line type="monotone" dataKey="response_time" stroke="#f59e0b" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </AnalyticsCard>
        <AnalyticsCard title="AI impact" subtitle="Savings generated by automation type">
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={charts.aiSavings}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#9ca3af" tickFormatter={(value) => format(new Date(value), 'MM/dd')} />
              <YAxis stroke="#9ca3af" />
              <Tooltip />
              <Area type="monotone" dataKey="triage" stroke="#10b981" fill="rgba(16,185,129,0.2)" strokeWidth={2} />
              <Area type="monotone" dataKey="drafting" stroke="#6366f1" fill="rgba(99,102,241,0.2)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </AnalyticsCard>
      </section>

      <section className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Metric Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricDetail label="Draft acceptance" value={`${analytics?.draft_metrics?.acceptance_rate || 0}%`} hint="of AI drafts sent without edits" />
          <MetricDetail label="Lead qualification" value={analytics?.lead_metrics?.qualified || 0} hint="Qualified in last 30 days" />
          <MetricDetail label="Tasks completed" value={`${analytics?.task_metrics?.completion_rate || 0}%`} hint="Completion percentage" />
          <MetricDetail label="Calendar sync" value={analytics?.calendar_metrics?.events_created || 0} hint="Events created from emails" />
        </div>
      </section>
    </div>
  )
}

function AnalyticsCard({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600">{subtitle}</p>
      </div>
      {children}
    </div>
  )
}

function MetricDetail({ label, value, hint }: { label: string; value: string | number; hint: string }) {
  return (
    <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-semibold text-gray-900 mt-2">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{hint}</p>
    </div>
  )
}

