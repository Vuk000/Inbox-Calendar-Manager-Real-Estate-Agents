import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { draftService } from '../services/api'
import toast from 'react-hot-toast'
import { SparklesIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline'

interface DraftGeneratorProps {
  messageId: number
  onDraftGenerated?: (drafts: any[]) => void
  onSend?: (draftId: number) => void
}

export default function DraftGenerator({ messageId, onDraftGenerated, onSend }: DraftGeneratorProps) {
  const [numVariants, setNumVariants] = useState(1)
  const [drafts, setDrafts] = useState<any[]>([])
  const [activeVariant, setActiveVariant] = useState(0)
  const [editMode, setEditMode] = useState(false)
  const [editedContent, setEditedContent] = useState('')

  const generateMutation = useMutation({
    mutationFn: () => draftService.generateDraft(messageId, numVariants),
    onSuccess: (data) => {
      setDrafts(data)
      setActiveVariant(0)
      setEditedContent(data[0]?.content || '')
      onDraftGenerated?.(data)
      toast.success(`Generated ${data.length} draft${data.length > 1 ? 's' : ''}!`)
    },
    onError: () => {
      toast.error('Failed to generate draft')
    },
  })

  const sendMutation = useMutation({
    mutationFn: (draftId: number) => draftService.sendDraft(draftId),
    onSuccess: () => {
      toast.success('Email sent successfully!')
      onSend?.(drafts[activeVariant].id)
    },
    onError: () => {
      toast.error('Failed to send email')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ draftId, content }: { draftId: number; content: string }) =>
      draftService.updateDraft(draftId, content),
    onSuccess: () => {
      toast.success('Draft updated')
      setEditMode(false)
    },
  })

  const handleGenerate = () => {
    generateMutation.mutate()
  }

  const handleSend = () => {
    const currentDraft = drafts[activeVariant]
    if (!currentDraft) return

    if (window.confirm('Are you sure you want to send this email?')) {
      sendMutation.mutate(currentDraft.id)
    }
  }

  const handleSaveEdit = () => {
    const currentDraft = drafts[activeVariant]
    if (!currentDraft) return

    updateMutation.mutate({
      draftId: currentDraft.id,
      content: editedContent,
    })
  }

  const currentDraft = drafts[activeVariant]

  return (
    <div className="space-y-4">
      {/* Generation controls */}
      {drafts.length === 0 ? (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <SparklesIcon className="h-5 w-5 text-primary-600 mr-2" />
            Generate AI Draft
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of variations
              </label>
              <select
                value={numVariants}
                onChange={(e) => setNumVariants(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value={1}>1 draft</option>
                <option value={2}>2 drafts (recommended)</option>
                <option value={3}>3 drafts</option>
              </select>
            </div>
            <button
              onClick={handleGenerate}
              disabled={generateMutation.isPending}
              className="btn-primary w-full disabled:opacity-50"
            >
              {generateMutation.isPending ? (
                <>
                  <span className="animate-spin inline-block mr-2">⚡</span>
                  Generating...
                </>
              ) : (
                <>
                  <SparklesIcon className="h-5 w-5 mr-2 inline" />
                  Generate Draft
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Variant tabs */}
          {drafts.length > 1 && (
            <div className="flex space-x-2 border-b border-gray-200">
              {drafts.map((draft, index) => (
                <button
                  key={draft.id}
                  onClick={() => {
                    setActiveVariant(index)
                    setEditedContent(draft.content)
                    setEditMode(false)
                  }}
                  className={`px-4 py-2 border-b-2 font-medium transition-colors ${
                    activeVariant === index
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Draft {index + 1}
                  {draft.confidence_score && (
                    <span className="ml-2 text-xs">
                      ({Math.round(draft.confidence_score * 100)}%)
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* Draft content */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Draft {activeVariant + 1}
              </h3>
              <div className="flex items-center space-x-2">
                {currentDraft?.confidence_score && (
                  <span className="text-sm text-gray-600">
                    Confidence: {Math.round(currentDraft.confidence_score * 100)}%
                  </span>
                )}
                <button
                  onClick={() => setEditMode(!editMode)}
                  className="btn-secondary text-sm"
                >
                  {editMode ? 'Cancel Edit' : 'Edit'}
                </button>
              </div>
            </div>

            {/* Subject line */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject
              </label>
              <input
                type="text"
                value={currentDraft?.subject || ''}
                readOnly
                className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>

            {/* Body */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message
              </label>
              {editMode ? (
                <textarea
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  rows={12}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 font-mono text-sm"
                />
              ) : (
                <div className="w-full px-4 py-3 border border-gray-200 rounded-lg bg-gray-50 whitespace-pre-wrap min-h-[200px]">
                  {currentDraft?.content}
                </div>
              )}
            </div>

            {/* Word count */}
            <div className="text-sm text-gray-500 mb-4">
              {currentDraft?.content?.split(/\s+/).length || 0} words
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-3">
              {editMode ? (
                <>
                  <button
                    onClick={handleSaveEdit}
                    disabled={updateMutation.isPending}
                    className="btn-primary"
                  >
                    {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                  </button>
                  <button
                    onClick={() => {
                      setEditMode(false)
                      setEditedContent(currentDraft?.content || '')
                    }}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={handleSend}
                    disabled={sendMutation.isPending}
                    className="btn-primary flex items-center"
                  >
                    <PaperAirplaneIcon className="h-5 w-5 mr-2" />
                    {sendMutation.isPending ? 'Sending...' : 'Send Email'}
                  </button>
                  <button
                    onClick={handleGenerate}
                    disabled={generateMutation.isPending}
                    className="btn-outline"
                  >
                    Regenerate
                  </button>
                </>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

