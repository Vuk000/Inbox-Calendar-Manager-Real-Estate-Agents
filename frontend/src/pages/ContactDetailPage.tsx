import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { contactsService, communicationsService } from '../services/api'
import { format } from 'date-fns'
import {
  ArrowLeftIcon,
  EnvelopeIcon,
  PhoneIcon,
  ChatBubbleLeftIcon,
  DocumentTextIcon,
  CalendarIcon,
  MapPinIcon,
  BuildingOfficeIcon,
  LinkIcon,
  PencilIcon,
} from '@heroicons/react/24/outline'
import { CommunicationLog, CommunicationType } from '../types/communication'

const communicationIcons: Record<CommunicationType, any> = {
  email: EnvelopeIcon,
  sms: ChatBubbleLeftIcon,
  whatsapp: ChatBubbleLeftIcon,
  phone_call: PhoneIcon,
  meeting: CalendarIcon,
  note: DocumentTextIcon,
  twitter_dm: ChatBubbleLeftIcon,
  facebook_messenger: ChatBubbleLeftIcon,
}

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>()
  const contactId = parseInt(id || '0')

  // Fetch contact details
  const { data: contact, isLoading: loadingContact } = useQuery({
    queryKey: ['contact', contactId],
    queryFn: () => contactsService.getContact(contactId),
    enabled: !!contactId,
  })

  // Fetch timeline
  const { data: timeline, isLoading: loadingTimeline } = useQuery({
    queryKey: ['contact-timeline', contactId],
    queryFn: () => contactsService.getContactTimeline(contactId),
    enabled: !!contactId,
  })

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['contact-stats', contactId],
    queryFn: () => communicationsService.getStats(contactId),
    enabled: !!contactId,
  })

  if (loadingContact) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!contact) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        Contact not found
      </div>
    )
  }

  const communications = timeline?.communications || []

  const getRelationshipColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-gray-600'
  }

  const getDirectionColor = (direction: string) => {
    return direction === 'inbound' ? 'border-blue-300 bg-blue-50' : 'border-gray-300 bg-gray-50'
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link to="/contacts" className="inline-flex items-center text-gray-600 hover:text-gray-900">
        <ArrowLeftIcon className="h-4 w-4 mr-2" />
        Back to Contacts
      </Link>

      {/* Contact Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0 h-20 w-20 rounded-full bg-primary-100 flex items-center justify-center">
              <span className="text-primary-700 font-bold text-2xl">
                {contact.first_name[0]}{contact.last_name?.[0] || ''}
              </span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {contact.first_name} {contact.last_name}
              </h1>
              {contact.company && (
                <p className="text-lg text-gray-600 flex items-center mt-1">
                  <BuildingOfficeIcon className="h-5 w-5 mr-2" />
                  {contact.company}
                  {contact.job_title && ` • ${contact.job_title}`}
                </p>
              )}
              <div className="flex items-center space-x-4 mt-3">
                {contact.email && (
                  <a href={`mailto:${contact.email}`} className="flex items-center text-gray-600 hover:text-primary-600">
                    <EnvelopeIcon className="h-4 w-4 mr-1" />
                    {contact.email}
                  </a>
                )}
                {contact.phone && (
                  <a href={`tel:${contact.phone}`} className="flex items-center text-gray-600 hover:text-primary-600">
                    <PhoneIcon className="h-4 w-4 mr-1" />
                    {contact.phone}
                  </a>
                )}
              </div>
              {(contact.city || contact.state) && (
                <p className="text-gray-500 flex items-center mt-2">
                  <MapPinIcon className="h-4 w-4 mr-1" />
                  {contact.city}{contact.city && contact.state && ', '}{contact.state}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm text-gray-500">Relationship Score</div>
              <div className={`text-4xl font-bold ${getRelationshipColor(contact.relationship_score)}`}>
                {Math.round(contact.relationship_score)}
              </div>
            </div>
            <Link to={`/contacts/${contactId}/edit`} className="btn-secondary">
              <PencilIcon className="h-5 w-5" />
            </Link>
          </div>
        </div>

        {/* Tags */}
        {contact.tags && contact.tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {contact.tags.map((tag, idx) => (
              <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Social Links */}
        {(contact.linkedin_url || contact.facebook_url || contact.twitter_handle) && (
          <div className="mt-4 flex items-center space-x-4">
            {contact.linkedin_url && (
              <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800">
                <LinkIcon className="h-5 w-5" />
              </a>
            )}
            {contact.facebook_url && (
              <a href={contact.facebook_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800">
                <LinkIcon className="h-5 w-5" />
              </a>
            )}
            {contact.twitter_handle && (
              <a href={`https://twitter.com/${contact.twitter_handle}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800">
                @{contact.twitter_handle}
              </a>
            )}
          </div>
        )}
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Total Communications</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stats.total_count}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Avg Sentiment</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">
              {stats.avg_sentiment !== null ? stats.avg_sentiment.toFixed(1) : 'N/A'}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Last Contact</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">
              {stats.last_contact ? format(new Date(stats.last_contact), 'MMM d') : 'Never'}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Frequency/Month</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">
              {stats.frequency_per_month.toFixed(1)}
            </div>
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Communication Timeline</h2>
          <p className="text-sm text-gray-600 mt-1">All interactions with this contact</p>
        </div>

        <div className="p-6">
          {loadingTimeline ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : communications.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <ChatBubbleLeftIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-4">No communications yet</p>
            </div>
          ) : (
            <div className="space-y-4">
              {communications.map((comm: CommunicationLog) => {
                const Icon = communicationIcons[comm.communication_type] || ChatBubbleLeftIcon
                return (
                  <div
                    key={comm.id}
                    className={`border-l-4 ${getDirectionColor(comm.direction)} rounded-lg p-4`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <div className="flex-shrink-0 p-2 bg-white rounded-lg border border-gray-200">
                          <Icon className="h-5 w-5 text-gray-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <span className="text-xs font-medium text-gray-500 uppercase">
                              {comm.communication_type.replace('_', ' ')}
                            </span>
                            <span className="text-xs text-gray-400">•</span>
                            <span className="text-xs text-gray-500 capitalize">
                              {comm.direction}
                            </span>
                          </div>
                          {comm.subject && (
                            <h4 className="text-sm font-medium text-gray-900 mt-1">
                              {comm.subject}
                            </h4>
                          )}
                          {comm.summary && (
                            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                              {comm.summary}
                            </p>
                          )}
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            {comm.from_address && (
                              <span>From: {comm.from_address}</span>
                            )}
                            {comm.sentiment_score !== null && (
                              <span>
                                Sentiment: {comm.sentiment_score > 0 ? '😊' : comm.sentiment_score < 0 ? '😞' : '😐'}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="text-sm text-gray-500 ml-4 flex-shrink-0">
                        {format(new Date(comm.occurred_at), 'MMM d, yyyy h:mm a')}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Notes */}
      {contact.notes && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Notes</h3>
          <p className="text-gray-700 whitespace-pre-wrap">{contact.notes}</p>
        </div>
      )}
    </div>
  )
}

