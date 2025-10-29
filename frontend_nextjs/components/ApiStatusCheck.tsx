"use client"

import { useEffect, useState } from "react"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import axios from "axios"

export function ApiStatusCheck() {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking")
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkApiStatus = async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
      
      try {
        // Try to hit the health endpoint
        const response = await axios.get(`${apiUrl.replace("/api/v1", "")}/health`, {
          timeout: 5000,
        })
        
        if (response.status === 200) {
          setStatus("online")
          setError(null)
        } else {
          setStatus("offline")
          setError("Backend returned non-200 status")
        }
      } catch (err: any) {
        setStatus("offline")
        setError(err.message || "Cannot reach backend server")
        console.error("[API Status] Backend unreachable:", err)
      }
    }

    checkApiStatus()
    // Check every 30 seconds
    const interval = setInterval(checkApiStatus, 30000)
    
    return () => clearInterval(interval)
  }, [])

  if (status === "checking") {
    return null // Don't show anything while checking
  }

  if (status === "offline") {
    return (
      <div className="fixed bottom-4 right-4 z-50 bg-destructive/90 text-destructive-foreground p-3 rounded-lg shadow-lg flex items-center gap-2 max-w-md">
        <AlertCircle className="w-5 h-5 flex-shrink-0" />
        <div className="flex-1">
          <p className="font-semibold text-sm">Backend Unreachable</p>
          <p className="text-xs opacity-90">{error}</p>
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

