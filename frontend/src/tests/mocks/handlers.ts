/**
 * MSW request handlers for API mocking
 */
import { http, HttpResponse } from 'msw'

const API_BASE_URL = 'http://localhost:8000/api/v1'

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE_URL}/auth/register`, async () => {
    return HttpResponse.json({
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      role: 'agent',
    }, { status: 201 })
  }),

  http.post(`${API_BASE_URL}/auth/login`, async () => {
    return HttpResponse.json({
      access_token: 'mock_access_token',
      token_type: 'bearer',
      user: {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'agent',
      },
    })
  }),

  http.get(`${API_BASE_URL}/auth/me`, async () => {
    return HttpResponse.json({
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
      role: 'agent',
      subscription_tier: 'professional',
    })
  }),

  // Email endpoints
  http.get(`${API_BASE_URL}/emails`, async () => {
    return HttpResponse.json({
      items: [
        {
          id: 1,
          subject: 'Property Inquiry',
          sender_email: 'client@example.com',
          sender_name: 'John Client',
          body: 'I am interested in viewing the property...',
          received_at: new Date().toISOString(),
          priority: 'high',
          category: 'lead',
          is_read: false,
        },
        {
          id: 2,
          subject: 'Offer on 123 Main St',
          sender_email: 'buyer@example.com',
          sender_name: 'Jane Buyer',
          body: 'I would like to submit an offer...',
          received_at: new Date().toISOString(),
          priority: 'high',
          category: 'offer',
          is_read: false,
        },
      ],
      total: 2,
      page: 1,
      page_size: 20,
    })
  }),

  http.get(`${API_BASE_URL}/emails/:id`, async ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      subject: 'Property Inquiry',
      sender_email: 'client@example.com',
      sender_name: 'John Client',
      body: 'I am interested in viewing the property at 123 Main Street. Can we schedule a showing?',
      received_at: new Date().toISOString(),
      priority: 'high',
      category: 'lead',
      is_read: false,
      triage_data: {
        priority: 'high',
        urgency_score: 85,
        category: 'lead',
        suggested_actions: ['reply', 'schedule'],
      },
    })
  }),

  http.post(`${API_BASE_URL}/emails/triage`, async () => {
    return HttpResponse.json({
      priority: 'high',
      urgency_score: 85,
      category: 'lead',
      entities: {
        property_addresses: ['123 Main Street'],
        dollar_amounts: [],
        dates: [],
        people: ['John Client'],
      },
      suggested_actions: ['reply', 'schedule'],
      sentiment_score: 0.8,
      key_points: [
        'Client interested in property viewing',
        'Requesting showing appointment',
      ],
      confidence: 0.92,
    })
  }),

  // Draft endpoints
  http.get(`${API_BASE_URL}/drafts`, async () => {
    return HttpResponse.json({
      items: [
        {
          id: 1,
          email_id: 1,
          content: 'Thank you for your inquiry...',
          status: 'pending',
          created_at: new Date().toISOString(),
        },
      ],
      total: 1,
    })
  }),

  http.post(`${API_BASE_URL}/drafts/generate`, async () => {
    return HttpResponse.json({
      id: 1,
      variants: [
        {
          variant_number: 1,
          content: 'Thank you for your interest in the property at 123 Main Street. I would be happy to schedule a showing for you. When would be a convenient time?',
          confidence_score: 0.88,
          word_count: 25,
        },
      ],
    })
  }),

  http.post(`${API_BASE_URL}/drafts/:id/approve`, async ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      status: 'approved',
      sent: true,
    })
  }),

  // Task endpoints
  http.get(`${API_BASE_URL}/tasks`, async () => {
    return HttpResponse.json({
      items: [
        {
          id: 1,
          title: 'Schedule showing for 123 Main St',
          description: 'Client requested property viewing',
          status: 'pending',
          priority: 'high',
          due_date: new Date(Date.now() + 86400000).toISOString(),
        },
        {
          id: 2,
          title: 'Follow up with buyer on offer',
          description: 'Check if buyer has questions',
          status: 'in_progress',
          priority: 'medium',
          due_date: new Date(Date.now() + 172800000).toISOString(),
        },
      ],
      total: 2,
    })
  }),

  http.post(`${API_BASE_URL}/tasks`, async () => {
    return HttpResponse.json({
      id: 3,
      title: 'New Task',
      status: 'pending',
      created_at: new Date().toISOString(),
    }, { status: 201 })
  }),

  http.patch(`${API_BASE_URL}/tasks/:id`, async ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      status: 'completed',
      updated_at: new Date().toISOString(),
    })
  }),

  // Analytics endpoints
  http.get(`${API_BASE_URL}/analytics/overview`, async () => {
    return HttpResponse.json({
      emails_processed: 1250,
      drafts_generated: 450,
      tasks_completed: 320,
      time_saved_hours: 42,
      lead_conversion_rate: 0.23,
      avg_response_time_hours: 1.5,
    })
  }),

  http.get(`${API_BASE_URL}/analytics/metrics/productivity`, async () => {
    return HttpResponse.json({
      emails_triaged: 1250,
      time_saved_hours: 42,
      lead_conversion_rate: 0.23,
      response_time_avg_hours: 1.5,
      period: '30d',
    })
  }),

  // Properties endpoints
  http.get(`${API_BASE_URL}/properties`, async () => {
    return HttpResponse.json({
      items: [
        {
          id: 1,
          address: '123 Main Street',
          city: 'Springfield',
          state: 'IL',
          zip: '62701',
          price: 350000,
          bedrooms: 3,
          bathrooms: 2,
          status: 'active',
        },
      ],
      total: 1,
    })
  }),

  // Integration endpoints
  http.get(`${API_BASE_URL}/integrations/gmail/connect`, async () => {
    return HttpResponse.json({
      authorization_url: 'https://accounts.google.com/o/oauth2/auth?...',
    })
  }),

  http.get(`${API_BASE_URL}/integrations/status`, async () => {
    return HttpResponse.json({
      gmail: { connected: true, last_sync: new Date().toISOString() },
      outlook: { connected: false, last_sync: null },
      twilio: { connected: true, last_sync: null },
    })
  }),
]

