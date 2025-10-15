import { useQuery } from '@tanstack/react-query'
import { emailService } from '../services/api'
import { format } from 'date-fns'
import DraftGenerator from './DraftGenerator'
import { useState } from 'react'
import { SparklesIcon, PaperAirplaneIcon, ChatBubbleOvalLeftEllipsisIcon } from '@heroicons/react/24/outline'

interface EmailDetailPanelProps {
  emailId: number
  onClose: () => void
}

export default function EmailDetailPanel({ emailId, onClose }: EmailDetailPanelProps) {
  const [showDrafts, setShowDrafts] = useState(false)

  const { data: email, isLoading, refetch } = useQuery({
    queryKey: ['email-detail', emailId],
    queryFn: () => emailService.getEmail(emailId)
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!email) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-600">Email not found.</p>
      </div>
    )
  }

  const handleGenerateDraft = () => {
    setShowDrafts(true)
  }

  return (
    <div className="flex flex-col h-full bg-white">
      <header className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">From {email.sender_name || email.sender_email}</p>
          <h2 className="text-xl font-semibold text-gray-900">{email.subject || '(No subject)'}</h2>
          <p className="text-xs text-gray-500">
            Received {format(new Date(email.received_at), 'PPpp')}
          </p>
        </div>
        <button onClick={onClose} className="btn-secondary">Close</button>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
        <section>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Message</h3>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 whitespace-pre-wrap text-sm text-gray-800">
            {email.body}
          </div>
        </section>

        <section>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">AI Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
              <h4 className="text-xs uppercase tracking-wide text-primary-600 font-semibold mb-1">Priority</h4>
              <p className="text-sm font-medium text-primary-900">{email.priority?.toUpperCase()}</p>
              <p className="text-xs text-primary-700">Urgency score {Math.round(email.urgency_score || 0)}%</p>
            </div>
            <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
              <h4 className="text-xs uppercase tracking-wide text-warning-600 font-semibold mb-1">Category</h4>
              <p className="text-sm font-medium text-warning-900">{email.category}</p>
              <p className="text-xs text-warning-700">Suggested actions: {email.suggested_actions.join(', ') || 'None'}</p>
            </div>
            <div className="col-span-1 md:col-span-2 bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h4 className="text-xs uppercase tracking-wide text-gray-600 font-semibold mb-1">Key Points</h4>
              <ul className="list-disc ml-4 text-sm text-gray-700 space-y-1">
                {email.entities?.property_addresses?.map((address: string) => (
                  <li key={address}>Property: {address}</li>
                ))}
                {email.entities?.dollar_amounts?.map((amount: string, idx: number) => (
                  <li key={`dollar-${idx}`}>Amount mentioned: {amount}</li>
                ))}
                {email.entities?.dates?.map((date: string, idx: number) => (
                  <li key={`date-${idx}`}>Date: {date}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section>
          <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
            <ChatBubbleOvalLeftEllipsisIcon className="h-4 w-4 text-primary-600 mr-2" /> Thread Context
          </h3>
          <div className="space-y-3">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <p className="text-xs text-gray-500">Most recent reply</p>
              <p className="text-sm text-gray-800">Thread rendering coming soon.</p>
            </div>
          </div>
        </section>
      </div>

      <footer className="border-t border-gray-200 px-6 py-4 bg-white">
        {showDrafts ? (
          <DraftGenerator messageId={emailId} onDraftGenerated={() => refetch()} />
        ) : (
          <div className="flex items-center space-x-3">
            <button onClick={handleGenerateDraft} className="btn-primary flex items-center">
              <SparklesIcon className="h-5 w-5 mr-2" /> Generate AI Reply
            </button>
            <button onClick={() => setShowDrafts(true)} className="btn-secondary flex items-center">
              <PaperAirplaneIcon className="h-5 w-5 mr-2" /> Compose manually
            </button>
          </div>
        )}
      </footer>
    </div>
  )
}
