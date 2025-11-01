"use client"

import React from "react"
import { AlertCircle, RefreshCw, WifiOff } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { checkBackendHealth } from "@/lib/api"

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  isBackendOffline: boolean
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<{ error: Error | null; resetError: () => void }>
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null, isBackendOffline: false }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error }
  }

  async componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo)
    
    // Check if error is related to backend connectivity
    const isNetworkError = error.message.includes("fetch") || 
                          error.message.includes("network") ||
                          error.message.includes("timeout") ||
                          error.message.includes("ECONNREFUSED")
    
    if (isNetworkError) {
      // Check if backend is actually offline
      try {
        const isHealthy = await checkBackendHealth()
        this.setState({ isBackendOffline: !isHealthy })
      } catch {
        this.setState({ isBackendOffline: true })
      }
    }
  }

  resetError = () => {
    this.setState({ hasError: false, error: null, isBackendOffline: false })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        const Fallback = this.props.fallback
        return <Fallback error={this.state.error} resetError={this.resetError} />
      }

      // Show backend offline message if backend is offline
      if (this.state.isBackendOffline) {
        return (
          <div className="flex items-center justify-center min-h-[400px] p-6">
            <Card className="glass-card max-w-md w-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-destructive">
                  <WifiOff className="w-5 h-5" />
                  Backend Server Offline
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  The backend server is not running. Please start the backend server to use this feature.
                </p>
                <div className="bg-muted p-3 rounded text-sm">
                  <p className="font-semibold mb-2">To start the backend:</p>
                  <ol className="list-decimal list-inside space-y-1">
                    <li>Open terminal in the <code className="bg-background px-1 rounded">backend</code> folder</li>
                    <li>Run: <code className="bg-background px-1 rounded">python -m uvicorn app.main:app --reload</code></li>
                  </ol>
                </div>
                <div className="flex gap-2">
                  <Button onClick={this.resetError} className="flex-1">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Try Again
                  </Button>
                  <Button variant="outline" onClick={() => window.location.reload()}>
                    Reload Page
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )
      }

      return (
        <div className="flex items-center justify-center min-h-[400px] p-6">
          <Card className="glass-card max-w-md w-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <AlertCircle className="w-5 h-5" />
                Something went wrong
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                    {this.state.error?.message || "An unexpected error occurred. Please try again."}
              </p>
              {process.env.NODE_ENV === "development" && this.state.error && (
                <details className="text-xs bg-muted p-3 rounded">
                  <summary className="cursor-pointer font-semibold mb-2">Error Details</summary>
                  <pre className="whitespace-pre-wrap overflow-auto max-h-40">
                    {this.state.error.stack}
                  </pre>
                </details>
              )}
              <div className="flex gap-2">
                <Button onClick={this.resetError} className="flex-1">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try Again
                </Button>
                <Button variant="outline" onClick={() => window.location.reload()}>
                  Reload Page
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}


