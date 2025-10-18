import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { contactsService } from '../services/api'
import { Contact } from '../types/contact'
import { Link } from 'react-router-dom'
import {
  UserGroupIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  ArrowUpTrayIcon,
  FunnelIcon,
  UserIcon,
} from '@heroicons/react/24/outline'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import ContactImportModal from '../components/ContactImportModal'

export default function ContactsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [contactType, setContactType] = useState<string>('')
  const [contactStatus, setContactStatus] = useState<string>('')
  const [showImportModal, setShowImportModal] = useState(false)
  
  const queryClient = useQueryClient()

  // Fetch contacts
  const { data, isLoading, error } = useQuery({
    queryKey: ['contacts', searchTerm, contactType, contactStatus],
    queryFn: () => contactsService.listContacts({
      search: searchTerm || undefined,
      contact_type: contactType || undefined,
      contact_status: contactStatus || undefined,
      limit: 100
    }),
  })

  const deleteContact = useMutation({
    mutationFn: (id: number) => contactsService.deleteContact(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] })
      toast.success('Contact deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete contact')
    }
  })

  const contacts = data?.contacts || []

  const handleDelete = (id: number, name: string) => {
    if (confirm(`Are you sure you want to delete ${name}?`)) {
      deleteContact.mutate(id)
    }
  }

  const getRelationshipColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50'
    if (score >= 50) return 'text-yellow-600 bg-yellow-50'
    return 'text-gray-600 bg-gray-50'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <UserGroupIcon className="h-8 w-8 mr-3 text-primary-600" />
            Contacts
          </h1>
          <p className="mt-2 text-gray-600">
            Manage your clients, leads, and professional network
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowImportModal(true)}
            className="btn-secondary flex items-center"
          >
            <ArrowUpTrayIcon className="h-5 w-5 mr-2" />
            Import CSV
          </button>
          <Link to="/contacts/new" className="btn-primary flex items-center">
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Contact
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search contacts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          <div>
            <select
              value={contactType}
              onChange={(e) => setContactType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Types</option>
              <option value="buyer">Buyer</option>
              <option value="seller">Seller</option>
              <option value="lead">Lead</option>
              <option value="agent">Agent</option>
              <option value="vendor">Vendor</option>
            </select>
          </div>
          <div>
            <select
              value={contactStatus}
              onChange={(e) => setContactStatus(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </div>
      </div>

      {/* Contacts List */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          Error loading contacts. Please try again.
        </div>
      ) : contacts.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No contacts found</h3>
          <p className="mt-2 text-gray-500">
            {searchTerm || contactType || contactStatus
              ? 'Try adjusting your filters'
              : 'Get started by adding your first contact'}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact Info
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Relationship Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Contact
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {contacts.map((contact: Contact) => (
                <tr key={contact.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link to={`/contacts/${contact.id}`} className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                        <span className="text-primary-700 font-medium">
                          {contact.first_name[0]}{contact.last_name?.[0] || ''}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900 hover:text-primary-600">
                          {contact.first_name} {contact.last_name}
                        </div>
                        {contact.company && (
                          <div className="text-sm text-gray-500">{contact.company}</div>
                        )}
                      </div>
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{contact.email || '-'}</div>
                    <div className="text-sm text-gray-500">{contact.phone || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 capitalize">
                      {contact.contact_type || 'Other'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRelationshipColor(contact.relationship_score)}`}>
                        {Math.round(contact.relationship_score)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {contact.last_contact_date
                      ? format(new Date(contact.last_contact_date), 'MMM d, yyyy')
                      : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                    <Link
                      to={`/contacts/${contact.id}`}
                      className="text-primary-600 hover:text-primary-900"
                    >
                      View
                    </Link>
                    <button
                      onClick={() => handleDelete(contact.id, `${contact.first_name} ${contact.last_name || ''}`)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Summary */}
      {contacts.length > 0 && (
        <div className="text-sm text-gray-600 text-center">
          Showing {contacts.length} contact{contacts.length !== 1 ? 's' : ''}
        </div>
      )}

      {/* Import Modal */}
      <ContactImportModal isOpen={showImportModal} onClose={() => setShowImportModal(false)} />
    </div>
  )
}

