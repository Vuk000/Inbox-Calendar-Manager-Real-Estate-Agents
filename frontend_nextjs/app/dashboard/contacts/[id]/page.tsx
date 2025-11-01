"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  ArrowLeft,
  Mail,
  Phone,
  MapPin,
  Calendar,
  MoreVertical,
  Edit,
  Trash2,
  Send,
  FileText,
  CheckCircle2,
  Clock,
  Video,
  DollarSign,
  Loader2,
  AlertCircle,
} from "lucide-react"
import { contactsService, communicationsService } from "@/lib/api"
import toast from "react-hot-toast"
import { formatDistanceToNow, format } from "date-fns"

export default function ContactDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [newNote, setNewNote] = useState("")

  // Fetch contact details
  const { data: contact, isLoading: isLoadingContact, error: contactError } = useQuery({
    queryKey: ['contact', params.id],
    queryFn: async () => {
      return await contactsService.getContact(parseInt(params.id))
    },
    enabled: !!params.id,
  })

  // Fetch communications timeline
  const { data: communications = [], isLoading: isLoadingTimeline } = useQuery({
    queryKey: ['communications', params.id],
    queryFn: async () => {
      const response = await communicationsService.listCommunications({
        contact_id: parseInt(params.id),
        limit: 100,
      })
      return Array.isArray(response) ? response : []
    },
    enabled: !!params.id,
  })

  // Delete contact mutation
  const deleteMutation = useMutation({
    mutationFn: async () => {
      await contactsService.deleteContact(parseInt(params.id))
    },
    onSuccess: () => {
      toast.success('Contact deleted successfully')
      router.push('/dashboard/contacts')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete contact')
    },
  })

  const handleDelete = () => {
    if (contact && confirm(`Are you sure you want to delete ${contact.full_name || contact.email}?`)) {
      deleteMutation.mutate()
    }
  }

  const getTimelineIcon = (type: string) => {
    switch (type) {
      case "email":
        return <Mail className="w-4 h-4" />
      case "phone_call":
        return <Phone className="w-4 h-4" />
      case "meeting":
        return <Video className="w-4 h-4" />
      case "note":
        return <FileText className="w-4 h-4" />
      case "sms":
        return <Phone className="w-4 h-4" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }

  const getTimelineColor = (type: string) => {
    switch (type) {
      case "email":
        return "bg-blue-500"
      case "phone_call":
      case "sms":
        return "bg-green-500"
      case "meeting":
        return "bg-purple-500"
      case "note":
        return "bg-yellow-500"
      default:
        return "bg-muted"
    }
  }

  if (isLoadingContact) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (contactError || !contact) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <AlertCircle className="w-8 h-8 text-destructive mb-4" />
        <p className="text-destructive">Failed to load contact</p>
        <Button variant="outline" className="mt-4" asChild>
          <Link href="/dashboard/contacts">Back to Contacts</Link>
        </Button>
      </div>
    )
  }

  // Format timeline events from communications
  const timelineEvents = communications.map((comm: any) => ({
    id: comm.id,
    type: comm.communication_type || 'email',
    title: comm.subject || `${comm.communication_type || 'Communication'} from ${comm.from_address || 'Unknown'}`,
    description: comm.summary || comm.body || 'No description available',
    timestamp: formatDistanceToNow(new Date(comm.occurred_at), { addSuffix: true }),
    date: format(new Date(comm.occurred_at), 'MMM d, yyyy h:mm a'),
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/dashboard/contacts">
            <ArrowLeft className="w-5 h-5" />
          </Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{contact.full_name || contact.email}</h1>
          <p className="text-muted-foreground mt-1">Contact details and interaction history</p>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="icon">
              <MoreVertical className="w-5 h-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => router.push(`/dashboard/contacts/${params.id}/edit`)}>
              <Edit className="w-4 h-4 mr-2" />
              Edit Contact
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Mail className="w-4 h-4 mr-2" />
              Send Email
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Calendar className="w-4 h-4 mr-2" />
              Schedule Meeting
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive" onClick={handleDelete}>
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Contact
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left column - Contact info */}
        <div className="space-y-6">
          {/* Profile card */}
          <Card className="glass-card">
            <CardContent className="p-6">
              <div className="flex flex-col items-center text-center space-y-4">
                <Avatar className="h-24 w-24">
                  <AvatarImage src={`/.jpg?height=96&width=96&query=${contact.full_name || contact.email}`} />
                  <AvatarFallback className="text-2xl">
                    {(contact.full_name || contact.email || "C")
                      .split(" ")
                      .map((n: string) => n[0])
                      .join("")
                      .toUpperCase()
                      .slice(0, 2)}
                  </AvatarFallback>
                </Avatar>
                <div className="space-y-1">
                  <h2 className="text-xl font-bold">{contact.full_name || contact.email}</h2>
                  <Badge variant={contact.contact_status === "hot_lead" ? "destructive" : "secondary"} className="text-xs">
                    {contact.contact_status?.replace(/_/g, " ") || "Active"}
                  </Badge>
                </div>
                {contact.tags && contact.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 justify-center">
                    {contact.tags.map((tag: string) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-6 space-y-3">
                <Button className="w-full glow-border">
                  <Mail className="w-4 h-4 mr-2" />
                  Send Email
                </Button>
                <Button variant="outline" className="w-full bg-transparent">
                  <Phone className="w-4 h-4 mr-2" />
                  Call Contact
                </Button>
                <Button variant="outline" className="w-full bg-transparent">
                  <Calendar className="w-4 h-4 mr-2" />
                  Schedule Meeting
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Contact details */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-lg">Contact Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Mail className="w-4 h-4" />
                  <span className="font-medium">Email</span>
                </div>
                <p className="text-sm pl-6">{contact.email || "Not provided"}</p>
              </div>
              {contact.phone && (
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Phone className="w-4 h-4" />
                    <span className="font-medium">Phone</span>
                  </div>
                  <p className="text-sm pl-6">{contact.phone}</p>
                </div>
              )}
              {(contact.city || contact.state) && (
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <MapPin className="w-4 h-4" />
                    <span className="font-medium">Location</span>
                  </div>
                  <p className="text-sm pl-6">{[contact.city, contact.state].filter(Boolean).join(", ") || "Not provided"}</p>
                </div>
              )}
              {contact.budget_max && (
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <DollarSign className="w-4 h-4" />
                    <span className="font-medium">Budget</span>
                  </div>
                  <p className="text-sm pl-6">
                    ${contact.budget_min?.toLocaleString() || "0"} - ${contact.budget_max?.toLocaleString() || "0"}
                  </p>
                </div>
              )}
              {contact.last_contact_date && (
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="w-4 h-4" />
                    <span className="font-medium">Last Contact</span>
                  </div>
                  <p className="text-sm pl-6">{formatDistanceToNow(new Date(contact.last_contact_date), { addSuffix: true })}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Additional info */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-lg">Additional Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {contact.lead_source && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Source</span>
                  <span className="font-medium">{contact.lead_source.replace(/_/g, " ")}</span>
                </div>
              )}
              {contact.created_at && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Created</span>
                  <span className="font-medium">{format(new Date(contact.created_at), "MMM d, yyyy")}</span>
                </div>
              )}
              {contact.relationship_score !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Relationship Score</span>
                  <span className="font-medium">{Math.round(contact.relationship_score)}%</span>
                </div>
              )}
              {contact.last_contact_date && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last contact</span>
                  <span className="font-medium">{formatDistanceToNow(new Date(contact.last_contact_date), { addSuffix: true })}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right column - Timeline and tabs */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="timeline" className="space-y-6">
            <TabsList className="glass-card">
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
              <TabsTrigger value="notes">Notes</TabsTrigger>
              <TabsTrigger value="tasks">Tasks</TabsTrigger>
              <TabsTrigger value="properties">Properties</TabsTrigger>
            </TabsList>

            <TabsContent value="timeline" className="space-y-6">
              {/* Add new note */}
              <Card className="glass-card">
                <CardContent className="p-4">
                  <div className="space-y-3">
                    <Label htmlFor="new-note">Add a note or update</Label>
                    <Textarea
                      id="new-note"
                      placeholder="What happened with this contact?"
                      className="bg-background/50 min-h-[100px]"
                      value={newNote}
                      onChange={(e) => setNewNote(e.target.value)}
                    />
                    <div className="flex gap-2">
                      <Button className="glow-border">
                        <Send className="w-4 h-4 mr-2" />
                        Add Note
                      </Button>
                      <Button variant="outline" className="bg-transparent">
                        <Mail className="w-4 h-4 mr-2" />
                        Log Email
                      </Button>
                      <Button variant="outline" className="bg-transparent">
                        <Phone className="w-4 h-4 mr-2" />
                        Log Call
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Timeline */}
              {isLoadingTimeline ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                </div>
              ) : timelineEvents.length === 0 ? (
                <Card className="glass-card">
                  <CardContent className="p-6">
                    <p className="text-muted-foreground text-center py-8">No communications yet</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {timelineEvents.map((event, index) => (
                  <Card key={event.id} className="glass-card">
                    <CardContent className="p-6">
                      <div className="flex gap-4">
                        <div className="relative">
                          <div
                            className={`w-10 h-10 rounded-full ${getTimelineColor(event.type)} flex items-center justify-center text-white`}
                          >
                            {getTimelineIcon(event.type)}
                          </div>
                          {index < timelineEvents.length - 1 && (
                            <div className="absolute top-10 left-1/2 -translate-x-1/2 w-0.5 h-8 bg-border" />
                          )}
                        </div>
                        <div className="flex-1 space-y-2">
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <h3 className="font-semibold">{event.title}</h3>
                              <p className="text-sm text-muted-foreground mt-1">{event.description}</p>
                            </div>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem>Edit</DropdownMenuItem>
                                <DropdownMenuItem className="text-destructive">Delete</DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            <span>{event.date}</span>
                            <span>•</span>
                            <span>{event.timestamp}</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="notes" className="space-y-4">
              <Card className="glass-card">
                <CardContent className="p-6">
                  <p className="text-muted-foreground text-center py-8">Notes view coming soon</p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="tasks" className="space-y-4">
              <Card className="glass-card">
                <CardContent className="p-6">
                  <p className="text-muted-foreground text-center py-8">Tasks view coming soon</p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="properties" className="space-y-4">
              <Card className="glass-card">
                <CardContent className="p-6">
                  <p className="text-muted-foreground text-center py-8">Properties view coming soon</p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
