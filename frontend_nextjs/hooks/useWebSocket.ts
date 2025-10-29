"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import { useAuthStore, useAuthHydration } from "@/lib/stores/authStore"
import { areTokensValid } from "@/lib/utils/auth"
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
  } = options

  const { accessToken, refreshToken } = useAuthStore()
  const hasHydrated = useAuthHydration()
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const connect = useCallback(() => {
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

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws"
    const url = `${wsUrl}?token=${accessToken}`

    try {
      const ws = new WebSocket(url)

      ws.onopen = () => {
        console.log("[WebSocket] Connected")
        setIsConnected(true)
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
            toast.success(`New email: ${message.data.subject || "No subject"}`)
          } else if (message.type === "task_updated") {
            toast.success(`Task updated: ${message.data.title || "Task"}`)
          } else if (message.type === "urgent_email") {
            toast.error(`Urgent email: ${message.data.subject || "No subject"}`, {
              duration: 8000,
            })
          }
        } catch (error) {
          console.error("[WebSocket] Failed to parse message:", error)
        }
      }

      ws.onerror = (error) => {
        console.error("[WebSocket] Error:", error)
        onError?.(error as any)
      }

      ws.onclose = () => {
        console.log("[WebSocket] Disconnected")
        setIsConnected(false)
        onDisconnect?.()

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1
          console.log(
            `[WebSocket] Reconnecting (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`
          )
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        } else {
          console.error("[WebSocket] Max reconnection attempts reached")
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error("[WebSocket] Failed to create connection:", error)
    }
  }, [accessToken, onMessage, onError, onConnect, onDisconnect, reconnectInterval, maxReconnectAttempts])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
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
  }
}

