"use client"

import type React from "react"

import { useEffect, useState } from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import {
  Sparkles,
  Home,
  Users,
  Calendar,
  Mail,
  CheckSquare,
  BarChart3,
  Settings,
  Search,
  Bell,
  Menu,
  X,
  LogOut,
} from "lucide-react"
import { useQueryClient } from "@tanstack/react-query"
import { cn } from "@/lib/utils"
import { Suspense } from "react"
import { useAuthStore, useAuthHydration } from "@/lib/stores/authStore"
import { authService } from "@/lib/api"
import { areTokensValid, clearInvalidTokens } from "@/lib/utils/auth"
import toast from "react-hot-toast"
import { ApiStatusCheck } from "@/components/ApiStatusCheck"
import { useWebSocket } from "@/hooks/useWebSocket"
import { Loader2 } from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: Home },
  { name: "Contacts", href: "/dashboard/contacts", icon: Users },
  { name: "Calendar", href: "/dashboard/calendar", icon: Calendar },
  { name: "Inbox", href: "/dashboard/inbox", icon: Mail },
  { name: "Tasks", href: "/dashboard/tasks", icon: CheckSquare },
  { name: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const queryClient = useQueryClient()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, isAuthenticated, logout, accessToken, refreshToken } = useAuthStore()
  const hasHydrated = useAuthHydration()
  const [isVerifyingAuth, setIsVerifyingAuth] = useState(true)

  // Initialize WebSocket connection for real-time updates (only if authenticated and tokens valid)
  const shouldConnectWebSocket = hasHydrated && isAuthenticated && areTokensValid(accessToken, refreshToken)
  
  const { backendOnline } = useWebSocket({
    enabled: shouldConnectWebSocket,
    onMessage: (message) => {
      console.log("[Dashboard] WebSocket message:", message)
      
      // Handle different message types and invalidate relevant queries
      switch (message.type) {
        case "new_email":
        case "urgent_email":
        case "triage_complete":
          queryClient.invalidateQueries({ queryKey: ['emails'] })
          queryClient.invalidateQueries({ queryKey: ['emailStats'] })
          queryClient.invalidateQueries({ queryKey: ['analytics'] })
          break
        case "draft_ready":
          queryClient.invalidateQueries({ queryKey: ['drafts'] })
          break
        case "task_update":
          queryClient.invalidateQueries({ queryKey: ['tasks'] })
          break
        case "sync_status":
          // Show sync status toast if needed
          if (message.data?.status === "complete") {
            toast.success("Email sync completed")
          }
          break
        default:
          break
      }
    },
    onError: (error) => {
      // Only log errors if backend is supposed to be online
      // Errors when backend is offline are expected and handled silently
      if (backendOnline !== false) {
        console.error("[Dashboard] WebSocket error:", error)
      }
    },
    onConnect: () => {
      console.log("[Dashboard] WebSocket connected")
    },
    onDisconnect: () => {
      console.log("[Dashboard] WebSocket disconnected")
    },
  })

  // Verify authentication after hydration
  useEffect(() => {
    // Wait for hydration
    if (!hasHydrated) {
      setIsVerifyingAuth(true)
      return
    }

    setIsVerifyingAuth(false)

    // Check if user is authenticated and tokens are valid
    if (!isAuthenticated || !areTokensValid(accessToken, refreshToken)) {
      // Clear invalid tokens if they exist
      clearInvalidTokens()
      router.push("/login")
      return
    }
  }, [hasHydrated, isAuthenticated, accessToken, refreshToken, router])

  // Show loading state during hydration or auth verification
  if (isVerifyingAuth || !hasHydrated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  // Don't render dashboard if not authenticated (will redirect in useEffect)
  if (!isAuthenticated || !areTokensValid(accessToken, refreshToken)) {
    return null
  }

  const handleLogout = () => {
    authService.logout()
    logout()
    toast.success("Logged out successfully")
    router.push("/login")
  }

  // Get user initials for avatar
  const userInitials = user?.full_name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase() || "U"

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border transform transition-transform duration-200 ease-in-out lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-border">
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold text-foreground">AgentFlow</span>
            </Link>
            <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(false)}>
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                  )}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* User profile */}
          <div className="p-4 border-t border-border">
            <Suspense fallback={<div>Loading...</div>}>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="w-full justify-start gap-3 h-auto p-2">
                    <Avatar className="w-8 h-8">
                      <AvatarFallback>{userInitials}</AvatarFallback>
                    </Avatar>
                    <div className="flex flex-col items-start text-sm">
                      <span className="font-medium">{user?.full_name || "User"}</span>
                      <span className="text-xs text-muted-foreground">{user?.email || ""}</span>
                    </div>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>My Account</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard/settings">Profile</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard/settings">Billing</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard/settings">Team</Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                    <LogOut className="w-4 h-4 mr-2" />
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </Suspense>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-30 flex items-center h-16 px-4 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <Button variant="ghost" size="icon" className="lg:hidden mr-2" onClick={() => setSidebarOpen(true)}>
            <Menu className="w-5 h-5" />
          </Button>

          {/* Search */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input placeholder="Search contacts, emails, tasks..." className="pl-9 bg-accent/50" />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 ml-4">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full" />
            </Button>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          <Suspense fallback={<div>Loading...</div>}>{children}</Suspense>
        </main>
      </div>
      <ApiStatusCheck />
    </div>
  )
}
