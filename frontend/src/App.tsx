import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout'

// Lazy load pages for better performance
const LandingPage = lazy(() => import('./pages/LandingPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const InboxPage = lazy(() => import('./pages/InboxPage'))
const DraftsPage = lazy(() => import('./pages/DraftsPage'))
const TasksPage = lazy(() => import('./pages/TasksPage'))
const PropertiesPage = lazy(() => import('./pages/PropertiesPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))
const ContactsPage = lazy(() => import('./pages/ContactsPage'))
const ContactDetailPage = lazy(() => import('./pages/ContactDetailPage'))

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
)

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
      {/* Public landing page */}
      <Route 
        path="/" 
        element={!isAuthenticated ? <LandingPage /> : <Navigate to="/dashboard" />} 
      />
      
      {/* Public routes */}
      <Route 
        path="/login" 
        element={!isAuthenticated ? <LoginPage /> : <Navigate to="/dashboard" />} 
      />
      <Route 
        path="/register" 
        element={!isAuthenticated ? <RegisterPage /> : <Navigate to="/dashboard" />} 
      />

      {/* Protected routes */}
      <Route 
        element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/inbox" element={<InboxPage />} />
        <Route path="/drafts" element={<DraftsPage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/properties" element={<PropertiesPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/contacts" element={<ContactsPage />} />
        <Route path="/contacts/:id" element={<ContactDetailPage />} />
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Suspense>
  )
}

export default App

