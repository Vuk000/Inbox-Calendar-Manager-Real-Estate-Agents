import { useQuery } from '@tanstack/react-query'
import { draftService } from '../services/api'
import { DocumentTextIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'

export default function DraftsPage() {
  const { data: drafts, isLoading } = useQuery({
    queryKey: ['drafts'],
    queryFn: draftService.listDrafts,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const getStatusBadge = (status: string) => {
    const styles = {
      pending: 'bg-warning-100 text-warning-700 border-warning-200',
      approved: 'bg-success-100 text-success-700 border-success-200',
      edited: 'bg-primary-100 text-primary-700 border-primary-200',
      sent: 'bg-success-100 text-success-700 border-success-200',
      rejected: 'bg-danger-100 text-danger-700 border-danger-200'
    }
    return `px-2 py-1 text-xs font-medium rounded-full border ${styles[status as keyof typeof styles] || styles.pending}`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI-Generated Drafts</h2>
          <p className="text-gray-600 mt-1">Review and manage your email drafts</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Total Drafts</p>
          <p className="text-2xl font-bold text-gray-900">{drafts?.length || 0}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Pending</p>
          <p className="text-2xl font-bold text-warning-600">
            {drafts?.filter((d: any) => d.approval_status === 'pending').length || 0}
          </p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Sent</p>
          <p className="text-2xl font-bold text-success-600">
            {drafts?.filter((d: any) => d.approval_status === 'sent').length || 0}
          </p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Edited</p>
          <p className="text-2xl font-bold text-primary-600">
            {drafts?.filter((d: any) => d.approval_status === 'edited').length || 0}
          </p>
        </div>
      </div>

      {/* Drafts List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {drafts && drafts.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {drafts.map((draft: any) => (
              <div key={draft.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <DocumentTextIcon className="h-6 w-6 text-gray-400" />
                    <div>
                      <h3 className="font-semibold text-gray-900">{draft.subject}</h3>
                      <p className="text-sm text-gray-500">
                        Variant {draft.variant_number}
                        {draft.confidence_score && (
                          <span className="ml-2">
                            • {Math.round(draft.confidence_score * 100)}% confidence
                          </span>
                        )}
                      </p>
                    </div>
                  </div>
                  <span className={getStatusBadge(draft.approval_status)}>
                    {draft.approval_status.replace('_', ' ')}
                  </span>
                </div>

                {/* Preview */}
                <div className="bg-gray-50 rounded-lg p-4 mb-3">
                  <p className="text-sm text-gray-700 line-clamp-3 whitespace-pre-wrap">
                    {draft.content}
                  </p>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    Generated {formatDistanceToNow(new Date(draft.generated_at), { addSuffix: true })}
                  </div>
                  <div className="flex items-center space-x-2">
                    {draft.approval_status === 'pending' && (
                      <>
                        <button className="btn-secondary text-sm">Edit</button>
                        <button className="btn-primary text-sm flex items-center">
                          <PaperAirplaneIcon className="h-4 w-4 mr-1" />
                          Send
                        </button>
                      </>
                    )}
                    {draft.approval_status === 'sent' && (
                      <span className="text-sm text-success-600 font-medium">
                        ✓ Sent
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No drafts yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Generate AI drafts from your inbox to see them here
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

