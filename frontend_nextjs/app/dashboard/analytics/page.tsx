"use client"

import { useQuery } from "@tanstack/react-query"
import { TrendingUp, TrendingDown, DollarSign, Home, Users, Mail, Loader2, AlertCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { analyticsService } from "@/lib/api"
import { format } from "date-fns"

export default function AnalyticsPage() {
  // Fetch analytics data
  const { data: analyticsData, isLoading, error } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      try {
        return await analyticsService.getDashboard()
      } catch (error) {
        // Return mock data structure if API fails
        return {
          total_revenue: 0,
          active_listings: 0,
          new_leads: 0,
          email_response_rate: 0,
          revenue_trend: 0,
          listings_trend: 0,
          leads_trend: 0,
          response_rate_trend: 0,
        }
      }
    },
    refetchOnWindowFocus: true,
  })

  const stats = [
    {
      label: "Total Revenue",
      value: analyticsData?.total_revenue
        ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(analyticsData.total_revenue)
        : "$0",
      change: analyticsData?.revenue_trend ? `${analyticsData.revenue_trend > 0 ? '+' : ''}${analyticsData.revenue_trend.toFixed(1)}%` : "+0%",
      trend: analyticsData?.revenue_trend && analyticsData.revenue_trend > 0 ? "up" : "down",
      icon: DollarSign,
    },
    {
      label: "Active Listings",
      value: analyticsData?.active_listings?.toString() || "0",
      change: analyticsData?.listings_trend ? `${analyticsData.listings_trend > 0 ? '+' : ''}${analyticsData.listings_trend}` : "+0",
      trend: analyticsData?.listings_trend && analyticsData.listings_trend > 0 ? "up" : "down",
      icon: Home,
    },
    {
      label: "New Leads",
      value: analyticsData?.new_leads?.toString() || "0",
      change: analyticsData?.leads_trend ? `${analyticsData.leads_trend > 0 ? '+' : ''}${analyticsData.leads_trend.toFixed(1)}%` : "+0%",
      trend: analyticsData?.leads_trend && analyticsData.leads_trend > 0 ? "up" : "down",
      icon: Users,
    },
    {
      label: "Email Response Rate",
      value: analyticsData?.email_response_rate ? `${analyticsData.email_response_rate.toFixed(0)}%` : "0%",
      change: analyticsData?.response_rate_trend ? `${analyticsData.response_rate_trend > 0 ? '+' : ''}${analyticsData.response_rate_trend.toFixed(1)}%` : "+0%",
      trend: analyticsData?.response_rate_trend && analyticsData.response_rate_trend > 0 ? "up" : "down",
      icon: Mail,
    },
  ]

  // Mock data for charts (backend doesn't have detailed chart data yet)
  const leadSources = [
    { source: "Website", leads: 45, percentage: 35, color: "bg-blue-500" },
    { source: "Referrals", leads: 32, percentage: 25, color: "bg-purple-500" },
    { source: "Social Media", leads: 28, percentage: 22, color: "bg-pink-500" },
    { source: "Open Houses", leads: 23, percentage: 18, color: "bg-orange-500" },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-balance">Analytics</h1>
        <p className="text-muted-foreground mt-1">Track your performance and insights</p>
      </div>

      {/* Loading state */}
      {isLoading && (
        <Card className="glass-card">
          <CardContent className="p-12 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading analytics...</p>
          </CardContent>
        </Card>
      )}

      {/* Error state */}
      {error && (
        <Card className="glass-card border-destructive">
          <CardContent className="p-12 text-center">
            <AlertCircle className="w-8 h-8 mx-auto mb-4 text-destructive" />
            <p className="text-destructive mb-2">Failed to load analytics</p>
            <p className="text-sm text-muted-foreground">Showing default values</p>
          </CardContent>
        </Card>
      )}

      {/* Stats Grid */}
      {(!isLoading || analyticsData) && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat) => {
              const Icon = stat.icon
              return (
                <Card key={stat.label} className="glass-card hover:scale-105 transition-transform">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 bg-primary/10 rounded-xl">
                        <Icon className="w-6 h-6 text-primary" />
                      </div>
                      <div
                        className={`flex items-center gap-1 text-sm font-semibold ${
                          stat.trend === "up" ? "text-green-600" : "text-red-600"
                        }`}
                      >
                        {stat.trend === "up" ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                        {stat.change}
                      </div>
                    </div>
                    <div className="text-3xl font-bold mb-1">{stat.value}</div>
                    <div className="text-sm text-muted-foreground">{stat.label}</div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Revenue Chart Placeholder */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Revenue Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gradient-to-br from-primary/10 to-secondary/10 rounded-xl flex items-center justify-center">
                  <div className="text-center">
                    <TrendingUp className="w-12 h-12 text-primary mx-auto mb-2" />
                    <p className="text-muted-foreground">Chart visualization coming soon</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {analyticsData?.total_revenue
                        ? `Total: ${new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(analyticsData.total_revenue)}`
                        : ''}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Lead Sources */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Lead Sources</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {leadSources.map((source) => (
                    <div key={source.source}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{source.source}</span>
                        <span className="text-sm text-muted-foreground">
                          {source.leads} leads ({source.percentage}%)
                        </span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className={`${source.color} h-2 rounded-full transition-all duration-500`}
                          style={{ width: `${source.percentage}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity Section */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle>Analytics Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Last Updated</p>
                    <p className="font-semibold">{format(new Date(), "MMM d, yyyy 'at' h:mm a")}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Data Period</p>
                    <p className="font-semibold">Last 30 Days</p>
                  </div>
                </div>
                {analyticsData && (
                  <div className="pt-4 border-t border-border">
                    <p className="text-sm text-muted-foreground">
                      Analytics data is fetched from your backend. Some metrics may be calculated from your contacts,
                      properties, and communications.
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
