"use client"

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react"
import { checkBackendHealth, clearHealthCheckCache } from "@/lib/api"

interface BackendHealthContextType {
  isOnline: boolean | null
  isLoading: boolean
  checkHealth: () => Promise<boolean>
  lastChecked: number | null
}

const BackendHealthContext = createContext<BackendHealthContextType | undefined>(undefined)

export function BackendHealthProvider({ children }: { children: ReactNode }) {
  const [isOnline, setIsOnline] = useState<boolean | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [lastChecked, setLastChecked] = useState<number | null>(null)

  const checkHealth = useCallback(async () => {
    setIsLoading(true)
    try {
      const healthy = await checkBackendHealth()
      setIsOnline(healthy)
      setLastChecked(Date.now())
      return healthy
    } catch (error) {
      setIsOnline(false)
      setLastChecked(Date.now())
      return false
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    // Initial health check
    checkHealth()

    // Check health every 30 seconds, but only if we're online or unknown
    // If offline, check less frequently (every 60 seconds) to reduce load
    const interval = setInterval(() => {
      if (isOnline === false) {
        // Backend is offline - check less frequently
        setTimeout(() => checkHealth(), 60000)
      } else {
        // Backend is online or unknown - check normally
        checkHealth()
      }
    }, isOnline === false ? 60000 : 30000)

    return () => clearInterval(interval)
  }, [checkHealth, isOnline])

  // Clear cache when backend comes back online
  useEffect(() => {
    if (isOnline === true) {
      clearHealthCheckCache()
    }
  }, [isOnline])

  return (
    <BackendHealthContext.Provider value={{ isOnline, isLoading, checkHealth, lastChecked }}>
      {children}
    </BackendHealthContext.Provider>
  )
}

export function useBackendHealth() {
  const context = useContext(BackendHealthContext)
  if (context === undefined) {
    throw new Error("useBackendHealth must be used within a BackendHealthProvider")
  }
  return context
}

