"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import {
  Mail,
  Search,
  Star,
  Archive,
  Trash2,
  Forward,
  Reply,
  Sparkles,
  MoreVertical,
  Inbox,
  AlertCircle,
  Clock,
  Loader2,
} from "lucide-react"
import { emailService, draftService } from "@/lib/api"
import toast from "react-hot-toast"
import { formatDistanceToNow } from "date-fns"
import { useRouter } from "next/navigation"

interface Email {
  id: number
  from_address: string
  subject: string | null
  summary: string | null
  urgency_score: number | null
  sentiment_score: number | null
  has_attachments: boolean
  occurred_at: string
  contact_id: number | null
}

export default function InboxPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState("all")
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null)
  const [page, setPage] = useState(1)

  // Fetch emails
  const { data: emails = [], isLoading, error, refetch } = useQuery({
    queryKey: ['emails', { page, search: searchQuery, tab: activeTab }],
    queryFn: async () => {
      const params: any = {
        page,
        limit: 50,
      }
      
      if (searchQuery) {
        params.search = searchQuery
      }
      
      // Filter by urgency for urgent tab
      if (activeTab === 'urgent') {
        params.urgency_min = 70
      }
      
      const response = await emailService.listEmails(params)
      return Array.isArray(response) ? response : []
    },
    refetchOnWindowFocus: true,
  })

  // Fetch email stats
  const { data: stats } = useQuery({
    queryKey: ['emailStats'],
    queryFn: async () => {
      try {
        return await emailService.getEmailStats()
      } catch (error) {
        return { total: 0, unread: 0, urgent: 0 }
      }
    },
  })

  // Fetch full email details when selected
  const { data: emailDetails, isLoading: isLoadingDetails } = useQuery({
    queryKey: ['email', selectedEmail?.id],
    queryFn: async () => {
      if (!selectedEmail) return null
      return await emailService.getEmail(selectedEmail.id)
    },
    enabled: !!selectedEmail,
  })

  // Generate AI draft mutation
  const generateDraftMutation = useMutation({
    mutationFn: async (emailId: number) => {
      return await draftService.generateDraft(emailId, 3)
    },
    onSuccess: (data) => {
      toast.success("AI draft generated! Redirecting to drafts...")
      router.push("/dashboard/drafts")
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to generate draft")
    },
  })

  // Filter emails based on tab
  const filteredEmails = emails.filter((email: Email) => {
    if (activeTab === "unread") {
      // For now, consider emails with high urgency as unread
      return (email.urgency_score || 0) > 50
    }
    if (activeTab === "urgent") {
      return (email.urgency_score || 0) >= 70
    }
    if (activeTab === "starred") {
      // Backend doesn't have starred field yet, skip for now
      return true
    }
    return true
  })

  const getPriorityColor = (urgencyScore: number | null) => {
    if (!urgencyScore) return "secondary"
    if (urgencyScore >= 70) return "destructive"
    if (urgencyScore >= 40) return "default"
    return "secondary"
  }

  const getPriorityLabel = (urgencyScore: number | null) => {
    if (!urgencyScore) return "low"
    if (urgencyScore >= 70) return "high"
    if (urgencyScore >= 40) return "medium"
    return "low"
  }

  const handleGenerateDraft = () => {
    if (selectedEmail) {
      generateDraftMutation.mutate(selectedEmail.id)
    }
  }

  // Format sender name from email address
  const getSenderName = (emailAddress: string) => {
    const match = emailAddress.match(/^(.+?)\s*<(.+)>$/) || emailAddress.match(/^(.+)$/)
    return match ? (match[1] || match[0]).trim() : emailAddress.split('@')[0]
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-balance">Inbox</h1>
          <p className="text-muted-foreground mt-1">Manage and respond to your emails</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()}>
            <Mail className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{stats?.total || 0}</div>
            <p className="text-sm text-muted-foreground">Total Emails</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-primary">{stats?.unread || 0}</div>
            <p className="text-sm text-muted-foreground">Unread</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-destructive">{stats?.urgent || 0}</div>
            <p className="text-sm text-muted-foreground">Urgent</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">
              {filteredEmails.filter((e: Email) => (e.urgency_score || 0) >= 70).length}
            </div>
            <p className="text-sm text-muted-foreground">Requires Action</p>
          </CardContent>
        </Card>
      </div>

      {/* Email List and Detail */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Email List */}
        <Card className="glass-card lg:col-span-1">
          <CardHeader>
            <div className="space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search emails..."
                  className="pl-9 bg-background/50"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="unread">Unread</TabsTrigger>
                  <TabsTrigger value="urgent">Urgent</TabsTrigger>
                  <TabsTrigger value="starred">Starred</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-12 text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
                <p className="text-muted-foreground">Loading emails...</p>
              </div>
            ) : error ? (
              <div className="p-12 text-center">
                <AlertCircle className="w-8 h-8 mx-auto mb-4 text-destructive" />
                <p className="text-destructive mb-2">Failed to load emails</p>
                <Button variant="outline" size="sm" onClick={() => refetch()}>
                  Retry
                </Button>
              </div>
            ) : filteredEmails.length === 0 ? (
              <div className="p-12 text-center">
                <Mail className="w-8 h-8 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">No emails found</p>
              </div>
            ) : (
              <div className="divide-y divide-border max-h-[600px] overflow-y-auto">
                {filteredEmails.map((email: Email) => {
                  const senderName = getSenderName(email.from_address)
                  const initials = senderName.charAt(0).toUpperCase()
                  const timestamp = email.occurred_at
                    ? formatDistanceToNow(new Date(email.occurred_at), { addSuffix: true })
                    : "Recently"
                  const priority = getPriorityLabel(email.urgency_score)
                  const isUnread = (email.urgency_score || 0) > 50

                  return (
                    <button
                      key={email.id}
                      onClick={() => setSelectedEmail(email)}
                      className={`w-full text-left p-4 hover:bg-accent/50 transition-colors ${
                        selectedEmail?.id === email.id ? "bg-accent" : ""
                      } ${isUnread ? "bg-primary/5" : ""}`}
                    >
                      <div className="flex items-start gap-3">
                        <Avatar className="w-10 h-10 flex-shrink-0">
                          <AvatarFallback>{initials}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <p
                              className={`font-bold text-sm truncate ${isUnread ? "text-foreground" : "text-muted-foreground"}`}
                            >
                              {senderName}
                            </p>
                            <span className="text-xs text-muted-foreground flex-shrink-0 ml-2">{timestamp}</span>
                          </div>
                          <p className={`text-sm mb-1 truncate ${isUnread ? "font-bold" : "font-medium"}`}>
                            {email.subject || "(No subject)"}
                          </p>
                          <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                            {email.summary || "(No preview)"}
                          </p>
                          <div className="flex items-center gap-2 flex-wrap">
                            <Badge variant={getPriorityColor(email.urgency_score)} className="text-xs">
                              {priority}
                            </Badge>
                            {email.has_attachments && (
                              <Badge variant="outline" className="text-xs">
                                Attachment
                              </Badge>
                            )}
                            {email.urgency_score && email.urgency_score >= 70 && (
                              <AlertCircle className="w-3 h-3 text-destructive" />
                            )}
                          </div>
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Email Detail */}
        <Card className="glass-card lg:col-span-2">
          {selectedEmail ? (
            <>
              {isLoadingDetails ? (
                <CardContent className="p-12 text-center">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
                  <p className="text-muted-foreground">Loading email details...</p>
                </CardContent>
              ) : emailDetails ? (
                <>
                  <CardHeader className="border-b border-border">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4 flex-1">
                        <Avatar className="w-12 h-12">
                          <AvatarFallback>{getSenderName(emailDetails.from_address || "").charAt(0)}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <h3 className="text-xl font-black text-foreground mb-1">
                            {emailDetails.subject || "(No subject)"}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            From: <span className="font-semibold">{getSenderName(emailDetails.from_address || "")}</span>{" "}
                            &lt;{emailDetails.from_address}&gt;
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {emailDetails.occurred_at
                              ? formatDistanceToNow(new Date(emailDetails.occurred_at), { addSuffix: true })
                              : "Recently"}
                          </p>
                        </div>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Star className="w-4 h-4 mr-2" />
                            Star
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Archive className="w-4 h-4 mr-2" />
                            Archive
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-destructive">
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="prose max-w-none mb-8">
                      <p className="text-foreground leading-relaxed whitespace-pre-wrap">
                        {emailDetails.body || emailDetails.summary || "(No content)"}
                      </p>
                    </div>
                    {emailDetails.urgency_score && emailDetails.urgency_score >= 70 && (
                      <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                        <div className="flex items-center gap-2 text-destructive">
                          <AlertCircle className="w-4 h-4" />
                          <span className="font-semibold">Urgent Email</span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          Urgency Score: {Math.round(emailDetails.urgency_score)}%
                        </p>
                      </div>
                    )}
                    <div className="flex flex-wrap gap-3 pt-6 border-t border-border">
                      <Button
                        className="glow-border bg-primary hover:bg-primary/90"
                        onClick={handleGenerateDraft}
                        disabled={generateDraftMutation.isPending}
                      >
                        {generateDraftMutation.isPending ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Generating...
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4 mr-2" />
                            Generate AI Reply
                          </>
                        )}
                      </Button>
                      <Button variant="outline">
                        <Reply className="w-4 h-4 mr-2" />
                        Reply
                      </Button>
                      <Button variant="outline">
                        <Forward className="w-4 h-4 mr-2" />
                        Forward
                      </Button>
                      <Button variant="outline">
                        <Archive className="w-4 h-4 mr-2" />
                        Archive
                      </Button>
                    </div>
                  </CardContent>
                </>
              ) : (
                <CardContent className="p-12 text-center">
                  <AlertCircle className="w-8 h-8 mx-auto mb-4 text-destructive" />
                  <p className="text-destructive">Failed to load email details</p>
                </CardContent>
              )}
            </>
          ) : (
            <CardContent className="p-12 flex flex-col items-center justify-center text-center min-h-[600px]">
              <Mail className="w-16 h-16 text-muted-foreground mb-4" />
              <h3 className="text-xl font-bold text-foreground mb-2">No email selected</h3>
              <p className="text-muted-foreground">Select an email from the list to view its contents</p>
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  )
}
