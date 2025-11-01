"use client"

import { AlertCircle, RefreshCw } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface ErrorDisplayProps {
  error: Error | any
  title?: string
  onRetry?: () => void
  showDetails?: boolean
}

export function ErrorDisplay({ error, title = "Something went wrong", onRetry, showDetails = false }: ErrorDisplayProps) {
  const errorMessage = error?.response?.data?.detail || error?.message || "An unexpected error occurred. Please try again."
  const statusCode = error?.response?.status

  return (
    <div className="flex items-center justify-center min-h-[300px] p-6">
      <Card className="glass-card max-w-md w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertCircle className="w-5 h-5" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <p className="text-muted-foreground">{errorMessage}</p>
            {statusCode && (
              <p className="text-xs text-muted-foreground">Status Code: {statusCode}</p>
            )}
          </div>
          
          {(showDetails || process.env.NODE_ENV === "development") && error?.stack && (
            <details className="text-xs bg-muted p-3 rounded">
              <summary className="cursor-pointer font-semibold mb-2">Error Details</summary>
              <pre className="whitespace-pre-wrap overflow-auto max-h-40">
                {error.stack}
              </pre>
            </details>
          )}

          {onRetry && (
            <div className="flex gap-2">
              <Button onClick={onRetry} className="flex-1">
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

