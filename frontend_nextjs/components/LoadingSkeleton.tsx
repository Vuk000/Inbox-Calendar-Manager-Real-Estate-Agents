import { Card, CardContent, CardHeader } from "@/components/ui/card"

export function CardSkeleton() {
  return (
    <Card className="glass-card">
      <CardHeader>
        <div className="h-6 w-3/4 bg-muted animate-pulse rounded" />
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="h-4 w-full bg-muted animate-pulse rounded" />
          <div className="h-4 w-5/6 bg-muted animate-pulse rounded" />
        </div>
      </CardContent>
    </Card>
  )
}

export function ListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-4 border border-border rounded-lg">
          <div className="w-12 h-12 bg-muted animate-pulse rounded-full" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-1/3 bg-muted animate-pulse rounded" />
            <div className="h-3 w-1/2 bg-muted animate-pulse rounded" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="space-y-2">
      {/* Header */}
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="h-4 w-1/2 bg-muted animate-pulse rounded" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} className="grid gap-4" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
          {Array.from({ length: cols }).map((_, colIdx) => (
            <div key={colIdx} className="h-8 w-full bg-muted animate-pulse rounded" />
          ))}
        </div>
      ))}
    </div>
  )
}

export function PageSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="h-8 w-1/3 bg-muted animate-pulse rounded" />
        <div className="h-4 w-1/2 bg-muted animate-pulse rounded" />
      </div>
      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="glass-card">
            <CardContent className="p-4">
              <div className="h-8 w-16 bg-muted animate-pulse rounded mb-2" />
              <div className="h-4 w-24 bg-muted animate-pulse rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
      {/* Content */}
      <Card className="glass-card">
        <CardHeader>
          <div className="h-6 w-1/4 bg-muted animate-pulse rounded" />
        </CardHeader>
        <CardContent>
          <ListSkeleton count={5} />
        </CardContent>
      </Card>
    </div>
  )
}

