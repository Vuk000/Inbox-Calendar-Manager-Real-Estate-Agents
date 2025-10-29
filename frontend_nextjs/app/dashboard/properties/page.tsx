"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Home, MapPin, DollarSign, Bed, Bath, Square, Plus, Search, Filter, TrendingUp, Loader2, Trash2, Edit, AlertCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { propertiesService } from "@/lib/api"
import toast from "react-hot-toast"
import Image from "next/image"
import Link from "next/link"

interface Property {
  id: number
  address: string
  city: string | null
  state: string | null
  zip_code: string | null
  mls_id: string | null
  property_type: string | null
  list_price: number | null
  sale_price: number | null
  transaction_type: string | null
  transaction_status: string | null
  created_at: string
}

export default function PropertiesPage() {
  const queryClient = useQueryClient()
  const [view, setView] = useState<"grid" | "list">("grid")
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  // Fetch properties
  const { data: properties = [], isLoading, error, refetch } = useQuery({
    queryKey: ['properties', { status: statusFilter }],
    queryFn: async () => {
      const params: any = {}
      if (statusFilter !== 'all') {
        params.transaction_status = statusFilter
      }
      const response = await propertiesService.listProperties(params)
      return Array.isArray(response) ? response : []
    },
    refetchOnWindowFocus: true,
  })

  // Create property mutation
  const createPropertyMutation = useMutation({
    mutationFn: async (data: any) => {
      return await propertiesService.createProperty(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['properties'] })
      toast.success('Property created successfully')
      setIsDialogOpen(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create property')
    },
  })

  // Delete property mutation
  const deletePropertyMutation = useMutation({
    mutationFn: async (id: number) => {
      await propertiesService.deleteProperty(id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['properties'] })
      toast.success('Property deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete property')
    },
  })

  const filteredProperties = properties.filter((property: Property) => {
    const matchesSearch =
      !searchQuery ||
      property.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
      `${property.city || ''} ${property.state || ''}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
      property.mls_id?.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesSearch
  })

  const handleCreateProperty = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = {
      address: formData.get('address') as string,
      city: formData.get('city') as string || null,
      state: formData.get('state') as string || null,
      zip_code: formData.get('zip_code') as string || null,
      mls_id: formData.get('mls_id') as string || null,
      property_type: formData.get('property_type') as string || null,
      list_price: formData.get('list_price') ? parseFloat(formData.get('list_price') as string) : null,
      transaction_type: formData.get('transaction_type') as string || null,
    }
    createPropertyMutation.mutate(data)
  }

  const handleDeleteProperty = (id: number, address: string) => {
    if (confirm(`Are you sure you want to delete ${address}?`)) {
      deletePropertyMutation.mutate(id)
    }
  }

  const formatPrice = (price: number | null) => {
    if (!price) return "Price TBD"
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(price)
  }

  // Calculate stats
  const stats = {
    active: properties.filter((p: Property) => p.transaction_status === 'active').length,
    pending: properties.filter((p: Property) => p.transaction_status === 'pending').length,
    totalValue: properties.reduce((sum: number, p: Property) => sum + (p.list_price || 0), 0),
    avgPrice: properties.length > 0
      ? properties.reduce((sum: number, p: Property) => sum + (p.list_price || 0), 0) / properties.length
      : 0,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-balance">Properties</h1>
          <p className="text-muted-foreground mt-1">Manage your property listings</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="glow-border">
              <Plus className="w-4 h-4 mr-2" />
              Add Property
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Property</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateProperty} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="address">Address *</Label>
                <Input id="address" name="address" required />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  <Input id="city" name="city" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="state">State</Label>
                  <Input id="state" name="state" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="zip_code">Zip Code</Label>
                  <Input id="zip_code" name="zip_code" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="mls_id">MLS ID</Label>
                  <Input id="mls_id" name="mls_id" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="property_type">Property Type</Label>
                  <Select name="property_type">
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="single_family">Single Family</SelectItem>
                      <SelectItem value="condo">Condo</SelectItem>
                      <SelectItem value="townhouse">Townhouse</SelectItem>
                      <SelectItem value="multi_family">Multi-Family</SelectItem>
                      <SelectItem value="commercial">Commercial</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="list_price">List Price</Label>
                  <Input id="list_price" name="list_price" type="number" step="0.01" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="transaction_type">Transaction Type</Label>
                  <Select name="transaction_type">
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sale">Sale</SelectItem>
                      <SelectItem value="rental">Rental</SelectItem>
                      <SelectItem value="lease">Lease</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={createPropertyMutation.isPending}>
                  {createPropertyMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Property"
                  )}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center">
                <Home className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="text-2xl font-bold">{stats.active}</div>
            <p className="text-sm text-muted-foreground">Active Listings</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-purple-500 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="text-2xl font-bold">{stats.pending}</div>
            <p className="text-sm text-muted-foreground">Pending Sales</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-green-500 flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="text-2xl font-bold">{formatPrice(stats.totalValue)}</div>
            <p className="text-sm text-muted-foreground">Total Value</p>
          </CardContent>
        </Card>
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-orange-500 flex items-center justify-center">
                <MapPin className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="text-2xl font-bold">{formatPrice(stats.avgPrice)}</div>
            <p className="text-sm text-muted-foreground">Avg. Price</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="glass-card">
        <CardContent className="p-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search properties..."
                className="pl-9 bg-background/50"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px] bg-background/50">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="sold">Sold</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Loading state */}
      {isLoading && (
        <Card className="glass-card">
          <CardContent className="p-12 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading properties...</p>
          </CardContent>
        </Card>
      )}

      {/* Error state */}
      {error && (
        <Card className="glass-card border-destructive">
          <CardContent className="p-12 text-center">
            <AlertCircle className="w-8 h-8 mx-auto mb-4 text-destructive" />
            <p className="text-destructive mb-2">Failed to load properties</p>
            <Button variant="outline" onClick={() => refetch()}>
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Properties Grid */}
      {!isLoading && !error && (
        <>
          {filteredProperties.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredProperties.map((property: Property) => {
                const location = [property.city, property.state].filter(Boolean).join(', ') || 'Location TBD'
                const imageUrl = `/modern-house-exterior.png` // Placeholder - backend doesn't have images yet

                return (
                  <Card key={property.id} className="glass-card hover:glow-border transition-all duration-300 overflow-hidden">
                    <div className="relative h-48 w-full bg-muted">
                      <Image
                        src={imageUrl}
                        alt={property.address}
                        fill
                        className="object-cover"
                        onError={(e) => {
                          // Fallback to placeholder if image fails
                          e.currentTarget.src = '/placeholder.jpg'
                        }}
                      />
                    </div>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg mb-1">{property.address}</CardTitle>
                          <p className="text-sm text-muted-foreground">{location}</p>
                        </div>
                        <Badge
                          variant={
                            property.transaction_status === 'active'
                              ? 'default'
                              : property.transaction_status === 'pending'
                                ? 'secondary'
                                : 'outline'
                          }
                          className="capitalize"
                        >
                          {property.transaction_status || 'Active'}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-2xl font-bold">{formatPrice(property.list_price)}</span>
                          {property.mls_id && (
                            <span className="text-xs text-muted-foreground">MLS: {property.mls_id}</span>
                          )}
                        </div>
                        {property.property_type && (
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Badge variant="outline" className="capitalize">
                              {property.property_type.replace('_', ' ')}
                            </Badge>
                            {property.transaction_type && (
                              <Badge variant="outline" className="capitalize">
                                {property.transaction_type}
                              </Badge>
                            )}
                          </div>
                        )}
                        <div className="flex gap-2 pt-2 border-t border-border">
                          <Button variant="outline" size="sm" className="flex-1" asChild>
                            <Link href={`/dashboard/properties/${property.id}`}>
                              <Edit className="w-3 h-3 mr-1" />
                              View Details
                            </Link>
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteProperty(property.id, property.address)}
                            disabled={deletePropertyMutation.isPending}
                          >
                            <Trash2 className="w-3 h-3 text-destructive" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          ) : (
            <Card className="glass-card">
              <CardContent className="p-12 text-center">
                <Home className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-xl font-bold mb-2">No properties found</h3>
                <p className="text-muted-foreground mb-6">Create your first property listing to get started</p>
                <Button onClick={() => setIsDialogOpen(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Property
                </Button>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
