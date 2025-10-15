/**
 * Draft Editor Component with Monaco Editor
 * Phase 4.2: Draft Approval Workflow
 */
import { useState, useEffect } from 'react'
import { DraftVariant } from '../types'

// TODO: Install @monaco-editor/react
// For now, using textarea as placeholder
// npm install @monaco-editor/react

interface DraftEditorProps {
  draft: DraftVariant
  originalEmail?: {
    subject: string
    body: string
    sender: string
  }
  onApprove: (content: string, send: boolean) => void
  onReject: (reason?: string) => void
  onSave: (content: string) => void
}

export function DraftEditor({
  draft,
  originalEmail,
  onApprove,
  onReject,
  onSave,
}: DraftEditorProps) {
  const [content, setContent] = useState(draft.content)
  const [isModified, setIsModified] = useState(false)
  const [showDiff, setShowDiff] = useState(false)
  const [sendImmediately, setSendImmediately] = useState(false)

  useEffect(() => {
    setIsModified(content !== draft.content)
  }, [content, draft.content])

  const handleApprove = () => {
    onApprove(content, sendImmediately)
  }

  const handleReject = () => {
    const reason = prompt('Why are you rejecting this draft? (optional)')
    onReject(reason || undefined)
  }

  const handleSave = () => {
    onSave(content)
    setIsModified(false)
  }

  const wordCount = content.split(/\s+/).filter(Boolean).length
  const charCount = content.length
  const changes = content.length - draft.content.length

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div>
          <h3 className="text-lg font-semibold">Draft Editor</h3>
          <p className="text-sm text-gray-600">
            Variant {draft.variant_number} • Confidence: {Math.round(draft.confidence_score * 100)}%
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowDiff(!showDiff)}
            className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
          >
            {showDiff ? 'Hide' : 'Show'} Diff
          </button>
          
          {isModified && (
            <span className="text-sm text-orange-600 font-medium">
              Modified •
            </span>
          )}
          
          <span className="text-sm text-gray-600">
            {wordCount} words • {charCount} chars
            {changes !== 0 && ` (${changes > 0 ? '+' : ''}${changes})`}
          </span>
        </div>
      </div>

      {/* Original Email Context (if provided) */}
      {originalEmail && (
        <div className="p-4 bg-gray-50 border-b">
          <p className="text-xs font-medium text-gray-500 mb-1">Replying to:</p>
          <p className="text-sm">
            <span className="font-medium">From:</span> {originalEmail.sender}
          </p>
          <p className="text-sm">
            <span className="font-medium">Subject:</span> {originalEmail.subject}
          </p>
        </div>
      )}

      {/* Editor Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Main Editor */}
        <div className={`flex-1 ${showDiff ? 'w-1/2' : 'w-full'}`}>
          {/* TODO: Replace with Monaco Editor */}
          {/* import Editor from '@monaco-editor/react' */}
          {/* <Editor
            value={content}
            onChange={(value) => setContent(value || '')}
            language="plaintext"
            theme="vs-light"
            options={{
              minimap: { enabled: false },
              lineNumbers: 'off',
              wordWrap: 'on',
              fontSize: 14,
            }}
          /> */}
          
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full h-full p-4 border-none resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Edit your draft here..."
          />
        </div>

        {/* Diff Viewer (if enabled) */}
        {showDiff && (
          <div className="w-1/2 border-l bg-gray-50 p-4 overflow-auto">
            <h4 className="font-medium mb-2">Changes from Original</h4>
            
            {/* TODO: Implement proper diff viewer */}
            {/* Use react-diff-viewer or similar library */}
            <div className="space-y-2 text-sm">
              <div>
                <p className="font-medium text-gray-700">Original ({draft.content.length} chars):</p>
                <div className="bg-red-50 p-2 rounded mt-1 line-through opacity-75">
                  {draft.content.substring(0, 200)}
                  {draft.content.length > 200 && '...'}
                </div>
              </div>
              
              <div>
                <p className="font-medium text-gray-700">Modified ({content.length} chars):</p>
                <div className="bg-green-50 p-2 rounded mt-1">
                  {content.substring(0, 200)}
                  {content.length > 200 && '...'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AI Metadata */}
      {draft.has_call_to_action && (
        <div className="px-4 py-2 bg-blue-50 border-t border-blue-100">
          <span className="text-sm text-blue-700">
            ✓ Call-to-action detected in draft
          </span>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between p-4 border-t bg-gray-50">
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={sendImmediately}
              onChange={(e) => setSendImmediately(e.target.checked)}
              className="rounded"
            />
            Send immediately after approval
          </label>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={handleReject}
            className="px-4 py-2 text-sm border border-red-300 text-red-700 rounded hover:bg-red-50"
          >
            Reject
          </button>
          
          {isModified && (
            <button
              onClick={handleSave}
              className="px-4 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50"
            >
              Save Draft
            </button>
          )}
          
          <button
            onClick={handleApprove}
            className="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 font-medium"
          >
            {sendImmediately ? 'Approve & Send' : 'Approve'}
          </button>
        </div>
      </div>

      {/* Footer Info */}
      <div className="px-4 py-2 text-xs text-gray-500 border-t">
        Generated by {draft.model_version} at {new Date(draft.generated_at).toLocaleString()}
        {draft.error && (
          <span className="text-red-600 ml-2">• Error: {draft.error}</span>
        )}
      </div>

      {/* TODO Markers for Future Enhancements */}
      {/* TODO: Integrate Monaco Editor for syntax highlighting */}
      {/* TODO: Add proper diff viewer with line-by-line comparison */}
      {/* TODO: Implement voice tone training interface */}
      {/* TODO: Add A/B testing for draft variations */}
      {/* TODO: Spell check and grammar check integration */}
      {/* TODO: Template suggestions based on email type */}
    </div>
  )
}

