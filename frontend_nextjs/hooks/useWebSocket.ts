"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import { useAuthStore, useAuthHydration } from "@/lib/stores/authStore"
import { areTokensValid } from "@/lib/utils/auth"
import { checkBackendHealth } from "@/lib/api"
import toast from "react-hot-toast"

interface WebSocketMessage {
  type: string
  data: any
  timestamp?: string
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onError?: (error: Event) => void
  onConnect?: () => void
  onDisconnect?: () => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
  enabled?: boolean // Allow disabling the connection
  skipHealthCheck?: boolean // Skip health check (for testing)
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    onMessage,
    onError,
    onConnect,
    onDisconnect,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
    enabled = true,
    skipHealthCheck = false,
  } = options

  const { accessToken, refreshToken } = useAuthStore()
  const hasHydrated = useAuthHydration()
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const healthCheckTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const backendOnlineRef = useRef<boolean | null>(null)

  const connect = useCallback(async () => {
    // Don't connect if disabled
    if (!enabled) {
      console.log("[WebSocket] Connection disabled")
      return
    }

    // Wait for hydration
    if (!hasHydrated) {
      console.log("[WebSocket] Waiting for auth hydration...")
      return
    }

    // Check if tokens are valid
    if (!areTokensValid(accessToken, refreshToken)) {
      console.warn("[WebSocket] Invalid or expired tokens, skipping connection")
      return
    }

    if (!accessToken) {
      console.warn("[WebSocket] No access token available")
      return
    }

    // Check backend health before attempting connection (unless skipped)
    if (!skipHealthCheck) {
      const isHealthy = await checkBackendHealth()
      setBackendOnline(isHealthy)
      backendOnlineRef.current = isHealthy
      
      if (!isHealthy) {
        // Backend is offline - don't attempt connection, but schedule health check retry
        console.log("[WebSocket] Backend is offline, skipping connection attempt")
        
        // Schedule health check retry after a delay
        if (healthCheckTimeoutRef.current) {
          clearTimeout(healthCheckTimeoutRef.current)
        }
        healthCheckTimeoutRef.current = setTimeout(() => {
          connect()
        }, reconnectInterval)
        
        return
      }
    }

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws"
    const url = `${wsUrl}?token=${accessToken}`

    try {
      const ws = new WebSocket(url)

      ws.onopen = () => {
        console.log("[WebSocket] Connected")
        setIsConnected(true)
        setBackendOnline(true)
        backendOnlineRef.current = true
        reconnectAttemptsRef.current = 0
        onConnect?.()
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          console.log("[WebSocket] Message received:", message)
          setLastMessage(message)
          onMessage?.(message)

          // Handle specific message types
          if (message.type === "new_email") {
            toast.success(`New email: ${message.data?.subject || "No subject"}`, { duration: 4000 })
          } else if (message.type === "task_update") {
            toast.success(`Task updated: ${message.data?.title || "Task"}`, { duration: 3000 })
          } else if (message.type === "urgent_email") {
            toast.error(`Urgent email: ${message.data?.subject || "No subject"}`, {
              duration: 8000,
            })
          } else if (message.type === "draft_ready") {
            toast.success(`AI draft ready: ${message.data?.subject || "Draft"}`, { duration: 4000 })
          } else if (message.type === "sync_status" && message.data?.status === "complete") {
            toast.success("Email sync completed", { duration: 3000 })
          }
        } catch (error) {
          console.error("[WebSocket] Failed to parse message:", error)
        }
      }

      ws.onerror = (error) => {
        // Only log errors if backend is supposed to be online
        // Suppress errors when backend is known to be offline (expected behavior)
        if (backendOnlineRef.current !== false) {
          console.error("[WebSocket] Error:", error)
          onError?.(error as any)
        } else {
          // Backend is offline, this is expected - don't log as error
          console.log("[WebSocket] Connection error (backend offline)")
        }
      }

      ws.onclose = (event) => {
        console.log("[WebSocket] Disconnected", event.code)
        setIsConnected(false)
        onDisconnect?.()

        // Only attempt reconnection if backend was online
        // If backend is offline, we'll retry after health check
        if (backendOnlineRef.current !== false && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1
          console.log(
            `[WebSocket] Reconnecting (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`
          )
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        } else if (backendOnlineRef.current === false) {
          // Backend is offline - schedule health check retry
          console.log("[WebSocket] Backend offline, will retry after health check")
          if (healthCheckTimeoutRef.current) {
            clearTimeout(healthCheckTimeoutRef.current)
          }
          healthCheckTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        } else {
          console.log("[WebSocket] Max reconnection attempts reached")
        }
      }

      wsRef.current = ws
    } catch (error) {
      // Suppress errors when backend is known to be offline
      if (backendOnlineRef.current !== false) {
        console.error("[WebSocket] Failed to create connection:", error)
      } else {
        console.log("[WebSocket] Cannot create connection (backend offline)")
      }
    }
  }, [accessToken, refreshToken, enabled, hasHydrated, skipHealthCheck, reconnectInterval, maxReconnectAttempts, onMessage, onError, onConnect, onDisconnect])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (healthCheckTimeoutRef.current) {
      clearTimeout(healthCheckTimeoutRef.current)
      healthCheckTimeoutRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
  }, [])

  const sendMessage = useCallback(
    (message: WebSocketMessage) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(message))
        return true
      }
      console.warn("[WebSocket] Cannot send message: not connected")
      return false
    },
    []
  )

  useEffect(() => {
    // Only connect if enabled, hydrated, and tokens are valid
    if (enabled && hasHydrated && areTokensValid(accessToken, refreshToken)) {
      connect()
    } else {
      // Disconnect if conditions are not met
      disconnect()
    }

    return () => {
      disconnect()
    }
  }, [enabled, hasHydrated, accessToken, refreshToken, connect, disconnect])

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
    backendOnline,
  }
}


