"use client"

import { useState } from "react"
import Link from "next/link"
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
} from "lucide-react"

// Mock timeline data
const timelineEvents = [
  {
    id: 1,
    type: "email",
    title: "Email sent: Property viewing confirmation",
    description: "Confirmed viewing appointment for 123 Main St on Friday at 2 PM",
    timestamp: "2 hours ago",
    date: "Today, 2:30 PM",
  },
  {
    id: 2,
    type: "call",
    title: "Phone call: Initial consultation",
    description: "Discussed budget, preferences, and timeline. Client interested in 3-bed homes in downtown area.",
    timestamp: "1 day ago",
    date: "Yesterday, 10:15 AM",
  },
  {
    id: 3,
    type: "meeting",
    title: "In-person meeting at office",
    description: "Reviewed market analysis and discussed financing options. Client pre-approved for $500K.",
    timestamp: "3 days ago",
    date: "Monday, 3:00 PM",
  },
  {
    id: 4,
    type: "note",
    title: "Added note",
    description: "Client mentioned they need to move by end of quarter due to job relocation.",
    timestamp: "5 days ago",
    date: "Saturday, 11:20 AM",
  },
  {
    id: 5,
    type: "email",
    title: "Email received: Inquiry about listings",
    description: "Client asked about new listings in the Marina district. Sent 5 properties matching criteria.",
    timestamp: "1 week ago",
    date: "Last Thursday, 4:45 PM",
  },
  {
    id: 6,
    type: "task",
    title: "Task completed: Send market report",
    description: "Sent comprehensive market analysis for target neighborhoods.",
    timestamp: "1 week ago",
    date: "Last Wednesday, 9:30 AM",
  },
]

const getTimelineIcon = (type: string) => {
  switch (type) {
    case "email":
      return <Mail className="w-4 h-4" />
    case "call":
      return <Phone className="w-4 h-4" />
    case "meeting":
      return <Video className="w-4 h-4" />
    case "note":
      return <FileText className="w-4 h-4" />
    case "task":
      return <CheckCircle2 className="w-4 h-4" />
    default:
      return <Clock className="w-4 h-4" />
  }
}

const getTimelineColor = (type: string) => {
  switch (type) {
    case "email":
      return "bg-blue-500"
    case "call":
      return "bg-green-500"
    case "meeting":
      return "bg-purple-500"
    case "note":
      return "bg-yellow-500"
    case "task":
      return "bg-primary"
    default:
      return "bg-muted"
  }
}

export default function ContactDetailPage({ params }: { params: { id: string } }) {
  const [newNote, setNewNote] = useState("")

  // Mock contact data
  const contact = {
    id: params.id,
    name: "Sarah Johnson",
    email: "sarah.j@email.com",
    phone: "(555) 123-4567",
    location: "Los Angeles, CA",
    status: "Hot Lead",
    priority: "high",
    tags: ["Buyer", "First-time"],
    budget: "$400K - $500K",
    preferences: "3-bed, 2-bath, downtown area",
    timeline: "Next 3 months",
    source: "Website inquiry",
    assignedTo: "John Doe",
    createdAt: "Jan 15, 2025",
    lastContact: "2 hours ago",
  }

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
          <h1 className="text-3xl font-bold">{contact.name}</h1>
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
            <DropdownMenuItem>
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
            <DropdownMenuItem className="text-destructive">
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
                  <AvatarImage src={`/.jpg?height=96&width=96&query=${contact.name}`} />
                  <AvatarFallback className="text-2xl">
                    {contact.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </AvatarFallback>
                </Avatar>
                <div className="space-y-1">
                  <h2 className="text-xl font-bold">{contact.name}</h2>
                  <Badge variant={contact.priority === "high" ? "destructive" : "secondary"} className="text-xs">
                    {contact.status}
                  </Badge>
                </div>
                <div className="flex flex-wrap gap-1 justify-center">
                  {contact.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
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
                <p className="text-sm pl-6">{contact.email}</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Phone className="w-4 h-4" />
                  <span className="font-medium">Phone</span>
                </div>
                <p className="text-sm pl-6">{contact.phone}</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <MapPin className="w-4 h-4" />
                  <span className="font-medium">Location</span>
                </div>
                <p className="text-sm pl-6">{contact.location}</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <DollarSign className="w-4 h-4" />
                  <span className="font-medium">Budget</span>
                </div>
                <p className="text-sm pl-6">{contact.budget}</p>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span className="font-medium">Timeline</span>
                </div>
                <p className="text-sm pl-6">{contact.timeline}</p>
              </div>
            </CardContent>
          </Card>

          {/* Additional info */}
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-lg">Additional Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Source</span>
                <span className="font-medium">{contact.source}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Assigned to</span>
                <span className="font-medium">{contact.assignedTo}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Created</span>
                <span className="font-medium">{contact.createdAt}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last contact</span>
                <span className="font-medium">{contact.lastContact}</span>
              </div>
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
