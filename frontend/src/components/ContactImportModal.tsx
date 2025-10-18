import { useState, useRef } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { contactsService } from '../services/api'
import { XMarkIcon, ArrowUpTrayIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface ContactImportModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function ContactImportModal({ isOpen, onClose }: ContactImportModalProps) {
  const [file, setFile] = useState<File | null>(null)
  const [csvHeaders, setCsvHeaders] = useState<string[]>([])
  const [fieldMapping, setFieldMapping] = useState<Record<string, string>>({})
  const [importing, setImporting] = useState(false)
  const [result, setResult] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()

  const contactFields = [
    { value: '', label: 'Do not import' },
    { value: 'first_name', label: 'First Name' },
    { value: 'last_name', label: 'Last Name' },
    { value: 'email', label: 'Email' },
    { value: 'phone', label: 'Phone' },
    { value: 'company', label: 'Company' },
    { value: 'job_title', label: 'Job Title' },
    { value: 'address_line1', label: 'Address Line 1' },
    { value: 'city', label: 'City' },
    { value: 'state', label: 'State' },
    { value: 'zip_code', label: 'Zip Code' },
    { value: 'linkedin_url', label: 'LinkedIn URL' },
    { value: 'notes', label: 'Notes' },
  ]

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile)
      setResult(null)
      
      // Read CSV headers
      const reader = new FileReader()
      reader.onload = (event) => {
        const text = event.target?.result as string
        const lines = text.split('\n')
        if (lines.length > 0) {
          const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
          setCsvHeaders(headers)
          
          // Auto-map common fields
          const autoMapping: Record<string, string> = {}
          headers.forEach(header => {
            const lower = header.toLowerCase()
            if (lower.includes('first') && lower.includes('name')) {
              autoMapping['first_name'] = header
            } else if (lower.includes('last') && lower.includes('name')) {
              autoMapping['last_name'] = header
            } else if (lower === 'email' || lower.includes('e-mail')) {
              autoMapping['email'] = header
            } else if (lower === 'phone' || lower.includes('telephone')) {
              autoMapping['phone'] = header
            } else if (lower === 'company' || lower.includes('organization')) {
              autoMapping['company'] = header
            }
          })
          setFieldMapping(autoMapping)
        }
      }
      reader.readAsText(selectedFile)
    } else {
      toast.error('Please select a valid CSV file')
    }
  }

  const handleImport = async () => {
    if (!file || Object.keys(fieldMapping).length === 0) {
      toast.error('Please map at least one field')
      return
    }

    if (!fieldMapping['first_name']) {
      toast.error('First Name is required')
      return
    }

    setImporting(true)
    try {
      const result = await contactsService.importCSV(file, fieldMapping)
      setResult(result)
      queryClient.invalidateQueries({ queryKey: ['contacts'] })
      toast.success(`Imported ${result.imported_count} contacts successfully!`)
    } catch (error) {
      toast.error('Failed to import contacts')
      setResult({ success: false, error: 'Import failed' })
    } finally {
      setImporting(false)
    }
  }

  const handleClose = () => {
    setFile(null)
    setCsvHeaders([])
    setFieldMapping({})
    setResult(null)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Overlay */}
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={handleClose}></div>

        {/* Modal */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <ArrowUpTrayIcon className="h-6 w-6 mr-2 text-primary-600" />
              Import Contacts from CSV
            </h3>
            <button onClick={handleClose} className="text-gray-400 hover:text-gray-600">
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 space-y-4">
            {!result ? (
              <>
                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select CSV File
                  </label>
                  <div className="flex items-center space-x-3">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".csv"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="btn-secondary"
                    >
                      Choose File
                    </button>
                    {file && (
                      <span className="text-sm text-gray-600">{file.name}</span>
                    )}
                  </div>
                </div>

                {/* Field Mapping */}
                {csvHeaders.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Map CSV Columns to Contact Fields
                    </label>
                    <div className="bg-gray-50 rounded-lg p-4 space-y-3 max-h-96 overflow-y-auto">
                      {contactFields.filter(f => f.value).map(field => (
                        <div key={field.value} className="flex items-center space-x-3">
                          <div className="w-1/3 text-sm font-medium text-gray-700">
                            {field.label}
                            {field.value === 'first_name' && (
                              <span className="text-red-500 ml-1">*</span>
                            )}
                          </div>
                          <div className="flex-1">
                            <select
                              value={Object.entries(fieldMapping).find(([k, v]) => k === field.value)?.[1] || ''}
                              onChange={(e) => {
                                const newMapping = { ...fieldMapping }
                                if (e.target.value) {
                                  newMapping[field.value] = e.target.value
                                } else {
                                  delete newMapping[field.value]
                                }
                                setFieldMapping(newMapping)
                              }}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            >
                              <option value="">-- Select CSV Column --</option>
                              {csvHeaders.map(header => (
                                <option key={header} value={header}>{header}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      * First Name is required for all contacts
                    </p>
                  </div>
                )}
              </>
            ) : (
              /* Results */
              <div className="space-y-4">
                {result.success ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <CheckCircleIcon className="h-6 w-6 text-green-600 mr-3" />
                      <div>
                        <h4 className="font-semibold text-green-900">Import Successful!</h4>
                        <p className="text-sm text-green-700 mt-1">
                          {result.imported_count} contacts imported
                        </p>
                        {result.skipped_count > 0 && (
                          <p className="text-sm text-yellow-700 mt-1">
                            {result.skipped_count} contacts skipped (duplicates)
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <XCircleIcon className="h-6 w-6 text-red-600 mr-3" />
                      <div>
                        <h4 className="font-semibold text-red-900">Import Failed</h4>
                        <p className="text-sm text-red-700 mt-1">{result.error || 'Unknown error'}</p>
                      </div>
                    </div>
                  </div>
                )}

                {result.errors && result.errors.length > 0 && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h5 className="font-medium text-yellow-900 mb-2">Errors:</h5>
                    <ul className="text-sm text-yellow-700 space-y-1 max-h-40 overflow-y-auto">
                      {result.errors.map((error: string, idx: number) => (
                        <li key={idx}>• {error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
            {!result ? (
              <>
                <button onClick={handleClose} className="btn-secondary">
                  Cancel
                </button>
                <button
                  onClick={handleImport}
                  disabled={!file || importing || !fieldMapping['first_name']}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {importing ? 'Importing...' : 'Import Contacts'}
                </button>
              </>
            ) : (
              <button onClick={handleClose} className="btn-primary">
                Done
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

