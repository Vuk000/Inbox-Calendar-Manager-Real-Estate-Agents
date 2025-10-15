import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { emailService } from '../services/api'
import {
  EnvelopeIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  StarIcon,
  BoltIcon,
  ChatBubbleOvalLeftIcon,
  PhoneIcon
} from '@heroicons/react/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid'
import { formatDistanceToNow } from 'date-fns'
import { useDebounce } from '../hooks/useDebounce'

interface EmailInboxProps {
  onSelectEmail?: (emailId: number) => void
}

const channels: Record<string, { label: string; icon: React.ComponentType<any>; className: string }> = {
  email: { label: 'Email', icon: EnvelopeIcon, className: 'bg-primary-100 text-primary-700' },
  sms: { label: 'SMS', icon: PhoneIcon, className: 'bg-success-100 text-success-700' },
  whatsapp: { label: 'WhatsApp', icon: PhoneIcon, className: 'bg-success-100 text-success-700' },
  twitter_dm: { label: 'Twitter DM', icon: BoltIcon, className: 'bg-sky-100 text-sky-700' },
  facebook_messenger: { label: 'Messenger', icon: ChatBubbleOvalLeftIcon, className: 'bg-indigo-100 text-indigo-700' }
}

export default function EmailInbox({ onSelectEmail }: EmailInboxProps) {
  const [activeTab, setActiveTab] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const debouncedSearch = useDebounce(searchQuery, 300)

  const tabs = [
    { id: 'all', label: 'All', filter: {} },
    { id: 'urgent', label: 'Urgent', filter: { priority: 'high' } },
    { id: 'leads', label: 'Leads', filter: { category: 'lead' } },
    { id: 'offers', label: 'Offers', filter: { category: 'offer' } },
    { id: 'inspections', label: 'Inspections', filter: { category: 'inspection' } },
    { id: 'social', label: 'Social', filter: { source: 'social' } },
  ]

  const activeTabData = tabs.find(t => t.id === activeTab) || tabs[0]

  const queryParams = useMemo(() => ({
    page,
    limit: 50,
    ...activeTabData.filter,
    search: debouncedSearch || undefined
  }), [page, activeTabData, debouncedSearch])

  const { data: emails, isLoading } = useQuery({
    queryKey: ['emails', queryParams],
    queryFn: () => emailService.listEmails(queryParams),
    placeholderData: (previousData) => previousData
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
  }

  const getPriorityBadge = (priority: string) => {
    const styles = {
      high: 'priority-high',
      medium: 'priority-medium',
      low: 'priority-low'
    }
    return `px-2 py-1 text-xs font-medium rounded-full border ${styles[priority as keyof typeof styles] || styles.low}`
  }

  const getCategoryBadge = (category: string) => {
    const styles = {
      offer: 'category-offer',
      lead: 'category-lead',
      inspection: 'category-inspection'
    }
    return `px-2 py-1 text-xs font-medium rounded-full border ${styles[category as keyof typeof styles] || 'bg-gray-100 text-gray-700 border-gray-200'}`
  }

  const renderChannelBadge = (source: string) => {
    const channel = channels[source] || channels.email
    const Icon = channel.icon
    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${channel.className}`}>
        <Icon className="h-3 w-3 mr-1" />
        {channel.label}
      </span>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-4 flex-wrap gap-3">
        <form onSubmit={handleSearch} className="flex-1 min-w-[220px]">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by subject, sender, property, or channel..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </form>
        <button className="btn-secondary flex items-center">
          <FunnelIcon className="h-5 w-5 mr-2" />
          Filters
        </button>
      </div>

      <div className="border-b border-gray-200 overflow-x-auto">
        <nav className="-mb-px flex space-x-8 min-w-max">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id)
                setPage(1)
              }}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="space-y-2">
        {emails && Array.isArray(emails) && emails.length > 0 ? (
          emails.map((email: any) => (
            <article
              key={email.id}
              onClick={() => onSelectEmail?.(email.id)}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0 space-y-2">
                  <header className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {renderChannelBadge(email.source)}
                      <span className={getPriorityBadge(email.priority)}>
                        {email.priority.toUpperCase()}
                      </span>
                      <span className={getCategoryBadge(email.category)}>
                        {email.category}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <span>{formatDistanceToNow(new Date(email.received_at), { addSuffix: true })}</span>
                      <button className="hover:text-warning-500" onClick={(e) => e.stopPropagation()}>
                        {email.is_starred ? (
                          <StarIconSolid className="h-5 w-5 text-warning-500" />
                        ) : (
                          <StarIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </header>

                  <div>
                    <p className="text-sm font-semibold text-gray-900">
                      {email.sender_name || email.sender_email}
                    </p>
                    <p className="text-xs text-gray-500">{email.sender_email}</p>
                  </div>

                  <h3 className={`text-base ${email.is_read ? 'text-gray-700' : 'text-gray-900 font-semibold'}`}>
                    {email.subject || '(No subject)'}
                  </h3>

                  <p className="text-sm text-gray-600 line-clamp-2">{email.body_preview}</p>

                  {email.urgency_score && (
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${email.urgency_score > 80 ? 'bg-danger-500' : email.urgency_score > 50 ? 'bg-warning-500' : 'bg-success-500'}`}
                          style={{ width: `${Math.min(email.urgency_score, 100)}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600">
                        {Math.round(email.urgency_score)}% urgent
                      </span>
                    </div>
                  )}
                </div>

                {email.has_attachments && (
                  <div className="ml-4 flex-shrink-0">
                    <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" />
                    </svg>
                  </div>
                )}
              </div>
            </article>
          ))
        ) : (
          <div className="text-center py-12">
            <EnvelopeIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No messages</h3>
            <p className="mt-1 text-sm text-gray-500">
              {activeTab === 'all' ? 'Your inbox is empty' : `No ${activeTab} messages found`}
            </p>
          </div>
        )}
      </div>

      {emails && Array.isArray(emails) && emails.length === 50 && (
        <div className="flex justify-center space-x-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-secondary disabled:opacity-50"
          >
            Previous
          </button>
          <span className="py-2 px-4 text-gray-700">Page {page}</span>
          <button
            onClick={() => setPage(p => p + 1)}
            className="btn-secondary"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

