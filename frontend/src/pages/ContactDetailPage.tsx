import { useParams, Link } from 'react-router-dom'
import { useInfiniteQuery, useQuery } from '@tanstack/react-query'
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
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar'
import 'react-circular-progressbar/dist/styles.css'
import { VerticalTimeline, VerticalTimelineElement } from 'react-vertical-timeline-component'
import 'react-vertical-timeline-component/style.min.css'
import { useState, useEffect } from 'react'
import { useInView } from 'react-intersection-observer'

const communicationConfig: Record<CommunicationType, { icon: any; color: string; bgColor: string }> = {
  email: { icon: EnvelopeIcon, color: '#2563eb', bgColor: '#eff6ff' },
  sms: { icon: ChatBubbleLeftIcon, color: '#10b981', bgColor: '#d1fae5' },
  whatsapp: { icon: ChatBubbleLeftIcon, color: '#10b981', bgColor: '#d1fae5' },
  phone_call: { icon: PhoneIcon, color: '#f59e0b', bgColor: '#fef3c7' },
  meeting: { icon: CalendarIcon, color: '#8b5cf6', bgColor: '#ede9fe' },
  note: { icon: DocumentTextIcon, color: '#eab308', bgColor: '#fef9c3' },
  twitter_dm: { icon: ChatBubbleLeftIcon, color: '#3b82f6', bgColor: '#dbeafe' },
  facebook_messenger: { icon: ChatBubbleLeftIcon, color: '#3b82f6', bgColor: '#dbeafe' },
}

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>()
  const contactId = parseInt(id || '0')
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set())

  // Intersection observer for infinite scroll
  const { ref: loadMoreRef, inView } = useInView({
    threshold: 0,
  })

  // Fetch contact details
  const { data: contact, isLoading: loadingContact } = useQuery({
    queryKey: ['contact', contactId],
    queryFn: () => contactsService.getContact(contactId),
    enabled: !!contactId,
  })

  // Fetch timeline with infinite scroll and cursor-based pagination
  const {
    data: timelinePages,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading: loadingTimeline,
  } = useInfiniteQuery({
    queryKey: ['contact-timeline', contactId],
    queryFn: ({ pageParam }) => contactsService.getContactTimeline(contactId, pageParam),
    enabled: !!contactId,
    getNextPageParam: (lastPage) => {
      // Return next cursor if there are more pages
      return lastPage?.pagination?.has_more ? lastPage.pagination.next_cursor : undefined
    },
    initialPageParam: undefined,
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

  // Load more when scrolled to bottom
  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage()
    }
  }, [inView, hasNextPage, isFetchingNextPage, fetchNextPage])

  if (!contact) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        Contact not found
      </div>
    )
  }

  // Flatten all pages into single array
  const communications = timelinePages?.pages.flatMap(page => page.communications) || []

  const getRelationshipScoreColor = (score: number) => {
    if (score >= 80) return { path: '#10b981', text: '#10b981', trail: '#d1fae5' }
    if (score >= 50) return { path: '#f59e0b', text: '#f59e0b', trail: '#fef3c7' }
    return { path: '#6b7280', text: '#6b7280', trail: '#f3f4f6' }
  }

  const getSentimentEmoji = (score: number | null) => {
    if (score === null) return '😐'
    if (score > 0.3) return '😊'
    if (score < -0.3) return '😞'
    return '😐'
  }

  const getSentimentColor = (score: number | null) => {
    if (score === null) return 'text-gray-500'
    if (score > 0.3) return 'text-green-600'
    if (score < -0.3) return 'text-red-600'
    return 'text-gray-500'
  }

  const toggleExpanded = (id: number) => {
    const newExpanded = new Set(expandedItems)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedItems(newExpanded)
  }

  const scoreColors = getRelationshipScoreColor(contact.relationship_score)

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
          <div className="flex items-start space-x-4 flex-1">
            <div className="flex-shrink-0 h-20 w-20 rounded-full bg-primary-100 flex items-center justify-center">
              <span className="text-primary-700 font-bold text-2xl">
                {contact.first_name[0]}{contact.last_name?.[0] || ''}
              </span>
            </div>
            <div className="flex-1">
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
          
          {/* Animated Relationship Score Gauge */}
          <div className="flex items-center space-x-6">
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-2">Relationship Score</div>
              <div style={{ width: 120, height: 120 }}>
                <CircularProgressbar
                  value={contact.relationship_score}
                  text={`${Math.round(contact.relationship_score)}`}
                  styles={buildStyles({
                    pathColor: scoreColors.path,
                    textColor: scoreColors.text,
                    trailColor: scoreColors.trail,
                    textSize: '20px',
                    pathTransitionDuration: 1.5,
                  })}
                />
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

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Total Communications</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stats.total_count}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Avg Sentiment</div>
            <div className="text-2xl font-bold text-gray-900 mt-1 flex items-center">
              {stats.avg_sentiment !== null ? stats.avg_sentiment.toFixed(1) : 'N/A'}
              <span className="ml-2 text-xl">{getSentimentEmoji(stats.avg_sentiment)}</span>
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

      {/* THE KILLER TIMELINE - Folio-inspired Visual Excellence */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Communication Timeline</h2>
          <p className="text-sm text-gray-600 mt-1">Every interaction, beautifully unified</p>
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
            <>
              <VerticalTimeline layout="1-column-left" lineColor="#e5e7eb">
                {communications.map((comm: CommunicationLog) => {
                  const config = communicationConfig[comm.communication_type]
                  const Icon = config.icon
                  const isExpanded = expandedItems.has(comm.id)

                  return (
                    <VerticalTimelineElement
                      key={comm.id}
                      date={format(new Date(comm.occurred_at), 'MMM d, yyyy h:mm a')}
                      iconStyle={{ background: config.color, color: '#fff' }}
                      icon={<Icon />}
                      contentStyle={{
                        background: config.bgColor,
                        border: `2px solid ${config.color}`,
                        borderRadius: '8px',
                        boxShadow: '0 3px 0 ' + config.color,
                        cursor: 'pointer',
                      }}
                      contentArrowStyle={{ borderRight: `7px solid ${config.color}` }}
                      onClick={() => toggleExpanded(comm.id)}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-medium uppercase" style={{ color: config.color }}>
                            {comm.communication_type.replace('_', ' ')} • {comm.direction}
                          </span>
                          {comm.sentiment_score !== null && (
                            <span className={`text-lg ${getSentimentColor(comm.sentiment_score)}`}>
                              {getSentimentEmoji(comm.sentiment_score)}
                            </span>
                          )}
                        </div>
                        
                        {comm.subject && (
                          <h4 className="text-sm font-semibold text-gray-900 mb-2">
                            {comm.subject}
                          </h4>
                        )}
                        
                        {comm.summary && (
                          <p className={`text-sm text-gray-700 ${!isExpanded ? 'line-clamp-2' : ''}`}>
                            {comm.summary}
                          </p>
                        )}
                        
                        {isExpanded && comm.summary && (
                          <div className="mt-2 pt-2 border-t border-gray-300">
                            <div className="text-xs text-gray-600 space-y-1">
                              {comm.from_address && <div>From: {comm.from_address}</div>}
                              {comm.to_address && <div>To: {comm.to_address}</div>}
                              {comm.urgency_score !== null && (
                                <div>Urgency: {Math.round(comm.urgency_score)}/100</div>
                              )}
                            </div>
                          </div>
                        )}
                        
                        <div className="text-xs text-gray-500 mt-2">
                          {isExpanded ? 'Click to collapse' : 'Click to expand'}
                        </div>
                      </div>
                    </VerticalTimelineElement>
                  )
                })}
              </VerticalTimeline>

              {/* Infinite scroll trigger */}
              {hasNextPage && (
                <div ref={loadMoreRef} className="py-8 text-center">
                  {isFetchingNextPage ? (
                    <div className="inline-flex items-center space-x-2 text-primary-600">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
                      <span className="text-sm">Loading more...</span>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500">Scroll to load more</div>
                  )}
                </div>
              )}

              {!hasNextPage && communications.length > 0 && (
                <div className="py-4 text-center text-sm text-gray-500">
                  End of timeline
                </div>
              )}
            </>
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

