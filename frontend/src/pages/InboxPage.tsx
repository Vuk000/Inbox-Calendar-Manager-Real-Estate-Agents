import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import EmailInbox from '../components/EmailInbox'
import EmailDetailPanel from '../components/EmailDetailPanel'
import { emailService } from '../services/api'
import { SparklesIcon, ExclamationTriangleIcon, ClockIcon, InboxIcon } from '@heroicons/react/24/outline'
import { useWebSocket } from '../hooks/useWebSocket'

export default function InboxPage() {
  const [selectedEmailId, setSelectedEmailId] = useState<number | null>(null)
  const [showDetail, setShowDetail] = useState(false)

  const { data: stats, refetch } = useQuery({
    queryKey: ['email-stats'],
    queryFn: () => emailService.getEmailStats()
  })

  useWebSocket((message) => {
    if (message.type === 'new_email' || message.type === 'sync_status') {
      refetch()
    }
  })

  const handleSelectEmail = (emailId: number) => {
    setSelectedEmailId(emailId)
    setShowDetail(true)
  }

  const handleCloseDetail = () => {
    setShowDetail(false)
    setSelectedEmailId(null)
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Emails"
          value={stats?.total ?? '--'}
          icon={InboxIcon}
          highlight="text-primary-600"
        />
        <StatCard
          title="Unread"
          value={stats?.unread ?? '--'}
          icon={ClockIcon}
          highlight="text-warning-600"
        />
        <StatCard
          title="Urgent"
          value={stats?.urgent ?? '--'}
          icon={ExclamationTriangleIcon}
          highlight="text-danger-600"
        />
        <StatCard
          title="Today"
          value={stats?.today ?? '--'}
          icon={SparklesIcon}
          highlight="text-success-600"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${showDetail ? 'xl:col-span-2' : 'xl:col-span-3'}`}>
          <EmailInbox onSelectEmail={handleSelectEmail} />
        </div>
        {showDetail && selectedEmailId && (
          <div className="hidden xl:block bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
            <EmailDetailPanel emailId={selectedEmailId} onClose={handleCloseDetail} />
          </div>
        )}
      </div>

      {showDetail && selectedEmailId && (
        <div className="xl:hidden fixed inset-0 bg-black/50 z-40 flex">
          <div className="relative w-full h-full bg-white">
            <EmailDetailPanel emailId={selectedEmailId} onClose={handleCloseDetail} />
          </div>
        </div>
      )}
    </div>
  )
}

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  highlight: string
}

function StatCard({ title, value, icon: Icon, highlight }: StatCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5 flex items-center justify-between shadow-sm">
      <div>
        <p className="text-sm text-gray-600">{title}</p>
        <p className={`text-2xl font-semibold mt-1 ${highlight}`}>{value}</p>
      </div>
      <div className="p-3 rounded-full bg-gray-100">
        <Icon className="h-6 w-6 text-gray-500" />
      </div>
    </div>
  )
}

