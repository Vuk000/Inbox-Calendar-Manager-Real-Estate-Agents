"use client"

import { useState } from "react"
import Link from "next/link"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Plus, MoreVertical, Mail, Phone, MapPin, Filter, ArrowUpDown, Loader2, Trash2, Edit } from "lucide-react"
import { contactsService } from "@/lib/api"
import toast from "react-hot-toast"
import { formatDistanceToNow } from "date-fns"
import { ContactCreateDialog } from "@/components/ContactCreateDialog"

export default function ContactsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const queryClient = useQueryClient()

  // Fetch contacts with React Query
  const { data: contactsData, isLoading, error } = useQuery({
    queryKey: ['contacts', { search: searchQuery, status: statusFilter }],
    queryFn: async () => {
      const params: any = {
        limit: 100,
      }
      if (searchQuery) {
        params.search = searchQuery
      }
      if (statusFilter !== 'all') {
        params.contact_status = statusFilter.toLowerCase().replace(' ', '_')
      }
      const response = await contactsService.listContacts(params)
      return response
    },
    refetchOnWindowFocus: true,
  })

  // Delete contact mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await contactsService.deleteContact(id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] })
      toast.success('Contact deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete contact')
    },
  })

  const contacts = contactsData?.contacts || []
  const total = contactsData?.total || 0

  // Calculate stats from contacts
  const stats = {
    total: total || contacts.length,
    hotLeads: contacts.filter((c: any) => c.contact_status === 'hot_lead').length,
    activeClients: contacts.filter((c: any) => c.contact_status === 'active' || c.contact_status === 'active_client').length,
    needFollowup: contacts.filter((c: any) => {
      if (!c.last_contact_date) return true
      const daysSince = Math.floor((Date.now() - new Date(c.last_contact_date).getTime()) / (1000 * 60 * 60 * 24))
      return daysSince > 7
    }).length,
  }

  const handleDelete = async (id: number, name: string) => {
    if (confirm(`Are you sure you want to delete ${name}?`)) {
      deleteMutation.mutate(id)
    }
  }

  // Filter contacts client-side for additional filtering
  const filteredContacts = contacts.filter((contact: any) => {
    const matchesSearch =
      !searchQuery ||
      `${contact.first_name || ''} ${contact.last_name || ''}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
      contact.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      `${contact.city || ''}, ${contact.state || ''}`.toLowerCase().includes(searchQuery.toLowerCase())

    return matchesSearch
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-balance">Contacts</h1>
          <p className="text-muted-foreground mt-1">Manage and organize your client relationships</p>
        </div>
        <Button className="glow-border" onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Contact
        </Button>
      </div>

      {/* Filters and search */}
      <Card className="glass-card">
        <CardContent className="p-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search contacts by name, email, or location..."
                className="pl-9 bg-background/50"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px] bg-background/50">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="hot_lead">Hot Lead</SelectItem>
                  <SelectItem value="active">Active Client</SelectItem>
                  <SelectItem value="follow_up">Follow-up</SelectItem>
                  <SelectItem value="cold_lead">Cold Lead</SelectItem>
                  <SelectItem value="contract_pending">Contract Pending</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" size="icon" className="bg-background/50">
                <ArrowUpDown className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-sm text-muted-foreground">Total Contacts</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{stats.hotLeads}</div>
            <p className="text-sm text-muted-foreground">Hot Leads</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{stats.activeClients}</div>
            <p className="text-sm text-muted-foreground">Active Clients</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{stats.needFollowup}</div>
            <p className="text-sm text-muted-foreground">Need Follow-up</p>
          </CardContent>
        </Card>
      </div>

      {/* Loading state */}
      {isLoading && (
        <Card className="glass-card">
          <CardContent className="p-12 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading contacts...</p>
          </CardContent>
        </Card>
      )}

      {/* Error state */}
      {error && (
        <Card className="glass-card border-destructive">
          <CardContent className="p-12 text-center">
            <p className="text-destructive mb-2">Failed to load contacts</p>
            <p className="text-sm text-muted-foreground">
              {(error as any)?.response?.data?.detail || (error as any)?.message || 'Unknown error'}
            </p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => queryClient.invalidateQueries({ queryKey: ['contacts'] })}
            >
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Contacts list */}
      {!isLoading && !error && (
        <>
          {filteredContacts.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredContacts.map((contact: any) => {
                const fullName = `${contact.first_name || ''} ${contact.last_name || ''}`.trim() || 'Unknown'
                const initials = fullName.split(' ').map((n: string) => n[0]).join('').toUpperCase()
                const location = [contact.city, contact.state].filter(Boolean).join(', ') || 'No location'
                const lastContact = contact.last_contact_date
                  ? formatDistanceToNow(new Date(contact.last_contact_date), { addSuffix: true })
                  : 'Never'
                const statusDisplay = contact.contact_status?.replace(/_/g, ' ') || 'Unknown'

                return (
                  <Card key={contact.id} className="glass-card hover:glow-border transition-all duration-300">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <Avatar className="h-12 w-12">
                            <AvatarFallback>{initials}</AvatarFallback>
                          </Avatar>
                          <div>
                            <Link href={`/dashboard/contacts/${contact.id}`}>
                              <h3 className="font-semibold hover:text-primary transition-colors">{fullName}</h3>
                            </Link>
                            <Badge
                              variant={
                                contact.contact_status === 'hot_lead'
                                  ? 'destructive'
                                  : contact.contact_status === 'active' || contact.contact_status === 'active_client'
                                    ? 'secondary'
                                    : 'outline'
                              }
                              className="text-xs mt-1 capitalize"
                            >
                              {statusDisplay}
                            </Badge>
                          </div>
                        </div>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem asChild>
                              <Link href={`/dashboard/contacts/${contact.id}`} className="flex items-center w-full">
                                View Details
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Mail className="w-4 h-4 mr-2" />
                              Send Email
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Phone className="w-4 h-4 mr-2" />
                              Schedule Meeting
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-destructive"
                              onClick={() => handleDelete(contact.id, fullName)}
                              disabled={deleteMutation.isPending}
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              {deleteMutation.isPending ? 'Deleting...' : 'Delete Contact'}
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>

                      <div className="space-y-2 text-sm">
                        {contact.email && (
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <Mail className="h-4 w-4" />
                            <span className="truncate">{contact.email}</span>
                          </div>
                        )}
                        {contact.phone_number && (
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <Phone className="h-4 w-4" />
                            <span>{contact.phone_number}</span>
                          </div>
                        )}
                        {location !== 'No location' && (
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <MapPin className="h-4 w-4" />
                            <span>{location}</span>
                          </div>
                        )}
                      </div>

                      <div className="mt-4 pt-4 border-t border-border">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-muted-foreground">Last contact: {lastContact}</span>
                        </div>
                        {contact.tags && contact.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {contact.tags.map((tag: string) => (
                              <Badge key={tag} variant="outline" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          ) : (
            <Card className="glass-card">
              <CardContent className="p-12 text-center">
                <p className="text-muted-foreground mb-4">No contacts found.</p>
                <Button onClick={() => setIsCreateDialogOpen(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Your First Contact
                </Button>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* Create Contact Dialog */}
      <ContactCreateDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onSuccess={() => {
          setIsCreateDialogOpen(false)
          queryClient.invalidateQueries({ queryKey: ['contacts'] })
        }}
      />
    </div>
  )
}
