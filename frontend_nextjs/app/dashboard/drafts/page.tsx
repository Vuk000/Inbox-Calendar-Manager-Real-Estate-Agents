"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Sparkles, Search, Send, Edit, Trash2, FileText, Plus, Loader2, AlertCircle } from "lucide-react"
import { draftService } from "@/lib/api"
import toast from "react-hot-toast"
import { formatDistanceToNow } from "date-fns"
import { useRouter } from "next/navigation"

interface Draft {
  id: number
  message_id: number
  subject: string
  content: string
  variant_number: number
  confidence_score: number | null
  approval_status: string
  generated_at: string
}

export default function DraftsPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [selectedDraft, setSelectedDraft] = useState<Draft | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [editedContent, setEditedContent] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  // Fetch drafts
  const { data: drafts = [], isLoading, error, refetch } = useQuery({
    queryKey: ['drafts'],
    queryFn: async () => {
      const response = await draftService.listDrafts()
      return Array.isArray(response) ? response : []
    },
    refetchOnWindowFocus: true,
  })

  // Group drafts by message_id to show variants together
  const groupedDrafts = drafts.reduce((acc: Record<number, Draft[]>, draft: Draft) => {
    if (!acc[draft.message_id]) {
      acc[draft.message_id] = []
    }
    acc[draft.message_id].push(draft)
    return acc
  }, {})

  // Update draft mutation
  const updateDraftMutation = useMutation({
    mutationFn: async ({ id, content }: { id: number; content: string }) => {
      return await draftService.updateDraft(id, content)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drafts'] })
      toast.success('Draft updated successfully')
      setIsDialogOpen(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update draft')
    },
  })

  // Delete draft mutation
  const deleteDraftMutation = useMutation({
    mutationFn: async (id: number) => {
      await draftService.deleteDraft(id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drafts'] })
      toast.success('Draft deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete draft')
    },
  })

  // Send draft mutation (placeholder - backend may not have this endpoint yet)
  const sendDraftMutation = useMutation({
    mutationFn: async (id: number) => {
      // TODO: Implement when backend adds send endpoint
      return await draftService.sendDraft(id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drafts'] })
      toast.success('Email sent successfully')
      setIsDialogOpen(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to send email')
    },
  })

  const filteredDrafts = Object.entries(groupedDrafts).filter(([messageId, variantDrafts]) => {
    const firstDraft = variantDrafts[0]
    return (
      firstDraft.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      firstDraft.content.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })

  const handleEditDraft = (draft: Draft) => {
    setSelectedDraft(draft)
    setEditedContent(draft.content)
    setIsDialogOpen(true)
  }

  const handleSaveDraft = () => {
    if (selectedDraft) {
      updateDraftMutation.mutate({ id: selectedDraft.id, content: editedContent })
    }
  }

  const handleSendDraft = () => {
    if (selectedDraft) {
      if (confirm('Are you sure you want to send this email?')) {
        sendDraftMutation.mutate(selectedDraft.id)
      }
    }
  }

  const handleDeleteDraft = (draftId: number) => {
    if (confirm('Are you sure you want to delete this draft?')) {
      deleteDraftMutation.mutate(draftId)
    }
  }

  const getConfidenceColor = (score: number | null) => {
    if (!score) return "secondary"
    if (score >= 80) return "default"
    if (score >= 60) return "secondary"
    return "outline"
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-black text-foreground mb-2">Email Drafts</h1>
          <p className="text-muted-foreground text-lg">AI-generated email drafts ready to send</p>
        </div>
        <Button
          className="glow-border bg-primary hover:bg-primary/90"
          onClick={() => router.push("/dashboard/inbox")}
        >
          <Plus className="w-4 h-4 mr-2" />
          Generate New Draft
        </Button>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Search drafts..."
          className="pl-9 bg-background/50"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Loading state */}
      {isLoading && (
        <Card className="glass-card">
          <CardContent className="p-12 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading drafts...</p>
          </CardContent>
        </Card>
      )}

      {/* Error state */}
      {error && (
        <Card className="glass-card border-destructive">
          <CardContent className="p-12 text-center">
            <AlertCircle className="w-8 h-8 mx-auto mb-4 text-destructive" />
            <p className="text-destructive mb-2">Failed to load drafts</p>
            <Button variant="outline" onClick={() => refetch()}>
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Drafts Grid */}
      {!isLoading && !error && (
        <>
          {filteredDrafts.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredDrafts.map(([messageId, variantDrafts]) => {
                const firstDraft = variantDrafts[0]
                const totalVariants = variantDrafts.length
                const timeAgo = formatDistanceToNow(new Date(firstDraft.generated_at), { addSuffix: true })

                return (
                  <Card key={messageId} className="glass-card hover:scale-105 transition-all duration-300">
                    <CardHeader>
                      <div className="flex items-start justify-between mb-2">
                        {totalVariants > 1 && (
                          <Badge variant="secondary" className="text-xs">
                            {totalVariants} Variants
                          </Badge>
                        )}
                        {firstDraft.confidence_score && (
                          <Badge variant={getConfidenceColor(firstDraft.confidence_score)} className="text-xs">
                            {Math.round(firstDraft.confidence_score)}% Confidence
                          </Badge>
                        )}
                      </div>
                      <CardTitle className="text-lg font-bold line-clamp-2">{firstDraft.subject}</CardTitle>
                      <p className="text-xs text-muted-foreground mt-1">{timeAgo}</p>
                      <Badge variant="outline" className="text-xs mt-2 capitalize">
                        {firstDraft.approval_status}
                      </Badge>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground line-clamp-4 mb-4 leading-relaxed whitespace-pre-line">
                        {firstDraft.content}
                      </p>
                      <div className="flex gap-2">
                        <Dialog open={isDialogOpen && selectedDraft?.id === firstDraft.id} onOpenChange={setIsDialogOpen}>
                          <DialogTrigger asChild>
                            <Button
                              variant="outline"
                              size="sm"
                              className="flex-1 bg-transparent"
                              onClick={() => handleEditDraft(firstDraft)}
                            >
                              <Edit className="w-3 h-3 mr-1" />
                              Edit
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
                            <DialogHeader>
                              <DialogTitle>{firstDraft.subject}</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                              {totalVariants > 1 ? (
                                <Tabs defaultValue={String(firstDraft.variant_number)}>
                                  <TabsList>
                                    {variantDrafts.map((draft) => (
                                      <TabsTrigger key={draft.id} value={String(draft.variant_number)}>
                                        Variant {draft.variant_number}
                                      </TabsTrigger>
                                    ))}
                                  </TabsList>
                                  {variantDrafts.map((draft) => (
                                    <TabsContent key={draft.id} value={String(draft.variant_number)}>
                                      <Textarea
                                        value={selectedDraft?.id === draft.id ? editedContent : draft.content}
                                        onChange={(e) => {
                                          setEditedContent(e.target.value)
                                          setSelectedDraft(draft)
                                        }}
                                        className="min-h-[300px] font-mono text-sm"
                                      />
                                      {draft.confidence_score && (
                                        <p className="text-xs text-muted-foreground mt-2">
                                          Confidence: {Math.round(draft.confidence_score)}%
                                        </p>
                                      )}
                                    </TabsContent>
                                  ))}
                                </Tabs>
                              ) : (
                                <>
                                  <Textarea
                                    value={editedContent}
                                    onChange={(e) => setEditedContent(e.target.value)}
                                    className="min-h-[300px] font-mono text-sm"
                                  />
                                  {firstDraft.confidence_score && (
                                    <p className="text-xs text-muted-foreground">
                                      Confidence: {Math.round(firstDraft.confidence_score)}%
                                    </p>
                                  )}
                                </>
                              )}
                              <div className="flex gap-3">
                                <Button
                                  className="flex-1 glow-border bg-primary hover:bg-primary/90"
                                  onClick={handleSendDraft}
                                  disabled={sendDraftMutation.isPending}
                                >
                                  {sendDraftMutation.isPending ? (
                                    <>
                                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                      Sending...
                                    </>
                                  ) : (
                                    <>
                                      <Send className="w-4 h-4 mr-2" />
                                      Send Email
                                    </>
                                  )}
                                </Button>
                                <Button
                                  variant="outline"
                                  onClick={handleSaveDraft}
                                  disabled={updateDraftMutation.isPending}
                                >
                                  {updateDraftMutation.isPending ? (
                                    <>
                                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                      Saving...
                                    </>
                                  ) : (
                                    "Save Changes"
                                  )}
                                </Button>
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="flex-shrink-0"
                          onClick={() => handleDeleteDraft(firstDraft.id)}
                          disabled={deleteDraftMutation.isPending}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          ) : (
            <Card className="glass-card">
              <CardContent className="p-12 flex flex-col items-center justify-center text-center">
                <FileText className="w-16 h-16 text-muted-foreground mb-4" />
                <h3 className="text-xl font-bold text-foreground mb-2">No drafts yet</h3>
                <p className="text-muted-foreground mb-6">
                  Generate your first AI draft from the inbox to get started
                </p>
                <Button
                  className="glow-border bg-primary hover:bg-primary/90"
                  onClick={() => router.push("/dashboard/inbox")}
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Go to Inbox
                </Button>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
