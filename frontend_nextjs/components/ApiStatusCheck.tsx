"use client"

import { useEffect, useState } from "react"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { checkBackendHealth, clearHealthCheckCache } from "@/lib/api"

let healthStatusListeners: Set<(status: "checking" | "online" | "offline", error: string | null) => void> = new Set()

export function useBackendStatus() {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking")
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const listener = (newStatus: "checking" | "online" | "offline", newError: string | null) => {
      setStatus(newStatus)
      setError(newError)
    }
    healthStatusListeners.add(listener)
    return () => {
      healthStatusListeners.delete(listener)
    }
  }, [])

  return { status, error }
}

function notifyStatusListeners(status: "checking" | "online" | "offline", error: string | null) {
  healthStatusListeners.forEach(listener => listener(status, error))
}

export function ApiStatusCheck() {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking")
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkApiStatus = async () => {
      setStatus("checking")
      notifyStatusListeners("checking", null)
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
      
      // Construct base URL by removing /api/v1 if present
      // Health endpoint is at root level: http://localhost:8000/health
      const baseUrl = apiUrl.replace(/\/api\/v\d+$/, "")
      const healthUrl = `${baseUrl}/health`
      
      try {
        // Use the shared health check function
        const isHealthy = await checkBackendHealth()
        
        if (isHealthy) {
          setStatus("online")
          setError(null)
          notifyStatusListeners("online", null)
        } else {
          setStatus("offline")
          setError("Backend returned non-200 status")
          notifyStatusListeners("offline", "Backend returned non-200 status")
        }
      } catch (err: any) {
        setStatus("offline")
        const errorMsg = err.message || "Cannot reach backend server"
        setError(errorMsg)
        notifyStatusListeners("offline", errorMsg)
        // Don't log errors when backend is offline (expected behavior)
        if (process.env.NODE_ENV === "development") {
          console.log("[API Status] Backend unreachable:", errorMsg)
        }
      }
    }

    checkApiStatus()
    // Check every 30 seconds when online, every 60 seconds when offline
    const interval = setInterval(() => {
      if (status === "offline") {
        // Backend is offline - check less frequently
        setTimeout(checkApiStatus, 30000)
      } else {
        checkApiStatus()
      }
    }, status === "offline" ? 60000 : 30000)
    
    return () => clearInterval(interval)
  }, [status])

  if (status === "checking") {
    return null // Don't show anything while checking
  }

  if (status === "offline") {
    return (
      <div className="fixed bottom-4 right-4 z-50 bg-destructive/90 text-destructive-foreground p-3 rounded-lg shadow-lg flex items-start gap-2 max-w-md">
        <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1 space-y-1">
          <p className="font-semibold text-sm">Backend Server Not Running</p>
          <p className="text-xs opacity-90">{error}</p>
          <div className="text-xs mt-2 pt-2 border-t border-destructive/30">
            <p className="font-semibold mb-1">To start the backend:</p>
            <ol className="list-decimal list-inside space-y-0.5 opacity-90">
              <li>Open terminal in the <code className="bg-black/20 px-1 rounded">backend</code> folder</li>
              <li>Run: <code className="bg-black/20 px-1 rounded">python -m uvicorn app.main:app --reload</code></li>
            </ol>
          </div>
          <p className="text-xs mt-1 opacity-75">
            API URL: {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 bg-primary/90 text-primary-foreground p-2 rounded-lg shadow-lg flex items-center gap-2">
      <CheckCircle2 className="w-4 h-4" />
      <Badge variant="secondary" className="bg-green-500 text-white">
        API Online
      </Badge>
    </div>
  )
}


