import axios, { AxiosInstance, AxiosError } from 'axios'
import { useAuthStore } from '../stores/authStore'
import toast from 'react-hot-toast'

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const { refreshToken } = useAuthStore.getState()
        
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token, user } = response.data
          const { login } = useAuthStore.getState()
          login(user, access_token, refreshToken)

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed - logout user
        const { logout } = useAuthStore.getState()
        logout()
        toast.error('Session expired. Please login again.')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // Handle other errors
    const errorMessage = 
      (error.response?.data as any)?.detail || 
      error.message || 
      'An error occurred'
    
    toast.error(errorMessage)
    return Promise.reject(error)
  }
)

export default api

// API service functions
export const authService = {
  register: async (data: { email: string; password: string; full_name: string }) => {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  login: async (data: { email: string; password: string }) => {
    const response = await api.post('/auth/login', data)
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout: () => {
    const { logout } = useAuthStore.getState()
    logout()
  },
}

export const emailService = {
  listEmails: async (params?: { 
    page?: number; 
    limit?: number; 
    priority?: string; 
    category?: string;
    source?: string;
    search?: string;
  }) => {
    const response = await api.get('/emails', { params })
    return response.data
  },

  getEmail: async (id: number) => {
    const response = await api.get(`/emails/${id}`)
    return response.data
  },

  searchEmails: async (query: string) => {
    const response = await api.post('/emails/search', { query })
    return response.data
  },

  getEmailStats: async () => {
    const response = await api.get('/emails/stats/summary')
    return response.data
  },

  toggleStar: async (id: number, starred: boolean) => {
    const response = await api.patch(`/emails/${id}/star`, null, { params: { starred } })
    return response.data
  }
}

export const draftService = {
  generateDraft: async (messageId: number, numVariants?: number) => {
    const response = await api.post('/drafts/generate', { 
      message_id: messageId,
      num_variants: numVariants || 1
    })
    return response.data
  },

  listDrafts: async () => {
    const response = await api.get('/drafts')
    return response.data
  },

  updateDraft: async (id: number, content: string) => {
    const response = await api.patch(`/drafts/${id}`, { content })
    return response.data
  },

  sendDraft: async (id: number) => {
    const response = await api.post(`/drafts/${id}/send`)
    return response.data
  },
}

export const taskService = {
  listTasks: async (params?: { status?: string }) => {
    const response = await api.get('/tasks', { params })
    return response.data
  },

  createTask: async (data: any) => {
    const response = await api.post('/tasks', data)
    return response.data
  },

  updateTask: async (id: number, data: any) => {
    const response = await api.patch(`/tasks/${id}`, data)
    return response.data
  },

  deleteTask: async (id: number) => {
    const response = await api.delete(`/tasks/${id}`)
    return response.data
  },
}

export const analyticsService = {
  getDashboard: async () => {
    const response = await api.get('/analytics/dashboard')
    return response.data
  },

  getReports: async (params?: { start_date?: string; end_date?: string }) => {
    const response = await api.get('/analytics/reports', { params })
    return response.data
  },
}

export const integrationService = {
  listSocialAccounts: async () => {
    const response = await api.get('/integrations/social-accounts')
    return response.data
  },
  listEmailAccounts: async () => {
    const response = await api.get('/integrations/email-accounts')
    return response.data
  },
  disconnectSocialAccount: async (id: number) => {
    const response = await api.delete(`/integrations/social-accounts/${id}`)
    return response.data
  },
  disconnectEmailAccount: async (id: number) => {
    const response = await api.delete(`/integrations/email-accounts/${id}`)
    return response.data
  }
}

