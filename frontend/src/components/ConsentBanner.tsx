/**
 * GDPR Consent Banner Component
 * Manages cookie and tracking consent
 */
import { useState, useEffect } from 'react'

interface ConsentBannerProps {
  onAccept?: () => void
  onReject?: () => void
}

export function ConsentBanner({ onAccept, onReject }: ConsentBannerProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Check if user has already consented
    const hasConsented = localStorage.getItem('gdpr_consent')
    if (!hasConsented) {
      setIsVisible(true)
    }
  }, [])

  const handleAccept = () => {
    localStorage.setItem('gdpr_consent', 'accepted')
    localStorage.setItem('gdpr_consent_date', new Date().toISOString())
    setIsVisible(false)
    onAccept?.()
  }

  const handleReject = () => {
    localStorage.setItem('gdpr_consent', 'rejected')
    localStorage.setItem('gdpr_consent_date', new Date().toISOString())
    setIsVisible(false)
    onReject?.()
  }

  if (!isVisible) {
    return null
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 text-white p-4 shadow-lg z-50">
      <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex-1">
          <h3 className="font-semibold mb-1">Cookie & Privacy Consent</h3>
          <p className="text-sm text-gray-300">
            We use cookies and similar technologies to improve your experience, analyze usage, 
            and provide personalized features. By clicking "Accept", you consent to our use of cookies 
            in accordance with our{' '}
            <a href="/privacy-policy" className="underline hover:text-blue-400">
              Privacy Policy
            </a>{' '}
            and{' '}
            <a href="/terms" className="underline hover:text-blue-400">
              Terms of Service
            </a>.
          </p>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={handleReject}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm font-medium transition-colors"
          >
            Reject
          </button>
          <button
            onClick={handleAccept}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-md text-sm font-medium transition-colors"
          >
            Accept All
          </button>
          <a
            href="/cookie-settings"
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm font-medium transition-colors"
          >
            Settings
          </a>
        </div>
      </div>
    </div>
  )
}

/**
 * Hook to check if user has consented
 */
export function useConsent() {
  const [hasConsented, setHasConsented] = useState<boolean | null>(null)

  useEffect(() => {
    const consent = localStorage.getItem('gdpr_consent')
    setHasConsented(consent === 'accepted')
  }, [])

  return {
    hasConsented,
    consentDate: localStorage.getItem('gdpr_consent_date'),
    revokeConsent: () => {
      localStorage.removeItem('gdpr_consent')
      localStorage.removeItem('gdpr_consent_date')
      setHasConsented(null)
    },
  }
}

