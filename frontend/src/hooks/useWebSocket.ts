import { useEffect, useRef, useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import toast from 'react-hot-toast'

interface WebSocketMessage {
  type: string
  data?: any
  message?: string
  status?: string
}

export function useWebSocket(onMessage?: (message: WebSocketMessage) => void) {
  const [isConnected, setIsConnected] = useState(false)
  const { accessToken } = useAuthStore()
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimeout = useRef<number>()

  useEffect(() => {
    if (!accessToken) return

    const connect = () => {
      const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws'
      ws.current = new WebSocket(`${wsUrl}?token=${accessToken}`)

      ws.current.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
      }

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          
          // Handle different message types
          switch (message.type) {
            case 'connected':
              console.log('WebSocket authenticated')
              break
            
            case 'new_email':
              toast.success('New email received!')
              break
            
            case 'draft_ready':
              toast.success('AI draft is ready!')
              break
            
            case 'sync_status':
              if (message.status === 'complete') {
                toast.success('Email sync complete')
              }
              break
            
            case 'task_update':
              toast('Task updated', { icon: 'ℹ️' })
              break
          }

          // Call custom handler
          if (onMessage) {
            onMessage(message)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.current.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        
        // Attempt reconnection after 5 seconds
        reconnectTimeout.current = setTimeout(() => {
          console.log('Reconnecting WebSocket...')
          connect()
        }, 5000)
      }
    }

    connect()

    // Cleanup on unmount
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current)
      }
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [accessToken])

  const sendMessage = (message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    }
  }

  return {
    isConnected,
    sendMessage
  }
}

