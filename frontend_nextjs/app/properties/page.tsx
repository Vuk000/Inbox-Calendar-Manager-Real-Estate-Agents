'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input, Textarea } from '@/components/ui/input';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { propertyAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { 
  Home, 
  Plus, 
  Edit, 
  Trash2, 
  Search,
  MapPin,
  DollarSign,
  Calendar,
  Building2
} from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { toast } from 'react-hot-toast';
import { Dialog } from '@/components/ui/drawer';
import { ConfirmationDialog } from '@/components/ui/drawer';
import { Select } from '@/components/ui/select';

interface Property {
  id: number;
  address: string;
  city?: string | null;
  state?: string | null;
  zip_code?: string | null;
  mls_id?: string | null;
  property_type?: string | null;
  list_price?: number | null;
  sale_price?: number | null;
  transaction_type?: string | null;
  transaction_status?: string | null;
  closing_date?: string | null;
  created_at: string;
}

export default function PropertiesPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isCreating, setIsCreating] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [deleteDialog, setDeleteDialog] = useState<{ id: number; address: string } | null>(null);

  const [formData, setFormData] = useState({
    address: '',
    city: '',
    state: '',
    zip_code: '',
    mls_id: '',
    property_type: '',
    list_price: '',
    transaction_type: '',
  });

  const { data: properties, isLoading, refetch } = useAPI(
    ['properties', statusFilter],
    () => {
      const params: any = {};
      if (statusFilter !== 'all') {
        params.transaction_status = statusFilter;
      }
      return propertyAPI.listProperties(params);
    },
    { enabled: isAuthenticated }
  );

  const filteredProperties = properties?.filter((p: Property) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      p.address.toLowerCase().includes(query) ||
      p.city?.toLowerCase().includes(query) ||
      p.mls_id?.toLowerCase().includes(query) ||
      p.zip_code?.toLowerCase().includes(query)
    );
  }) || [];

  const createMutation = useAPIMutation(
    (data: any) => propertyAPI.createProperty(data),
    {
      onSuccess: () => {
        toast.success('Property created');
        setIsCreating(false);
        resetForm();
        refetch();
      },
      onError: (error: any) => {
        toast.error(error?.response?.data?.detail || 'Failed to create property');
      },
    }
  );

  const updateMutation = useAPIMutation(
    ({ id, data }: { id: number; data: any }) => propertyAPI.updateProperty(id, data),
    {
      onSuccess: () => {
        toast.success('Property updated');
        setSelectedProperty(null);
        resetForm();
        refetch();
      },
    }
  );

  const resetForm = () => {
    setFormData({
      address: '',
      city: '',
      state: '',
      zip_code: '',
      mls_id: '',
      property_type: '',
      list_price: '',
      transaction_type: '',
    });
  };

  const handleCreate = () => {
    if (!formData.address.trim()) {
      toast.error('Address is required');
      return;
    }
    createMutation.mutate({
      address: formData.address,
      city: formData.city || undefined,
      state: formData.state || undefined,
      zip_code: formData.zip_code || undefined,
      mls_id: formData.mls_id || undefined,
      property_type: formData.property_type || undefined,
      list_price: formData.list_price ? parseFloat(formData.list_price) : undefined,
      transaction_type: formData.transaction_type || undefined,
    });
  };

  const handleUpdate = () => {
    if (!selectedProperty || !formData.address.trim()) {
      toast.error('Address is required');
      return;
    }
    updateMutation.mutate({
      id: selectedProperty.id,
      data: {
        address: formData.address,
        city: formData.city || undefined,
        state: formData.state || undefined,
        zip_code: formData.zip_code || undefined,
        list_price: formData.list_price ? parseFloat(formData.list_price) : undefined,
      },
    });
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatPrice = (price: number | null | undefined) => {
    if (!price) return 'N/A';
    return `$${price.toLocaleString()}`;
  };

  const getStatusBadge = (status: string | null | undefined) => {
    if (!status) return <Badge variant="default">Unknown</Badge>;
    switch (status.toLowerCase()) {
      case 'active':
        return <Badge variant="success">Active</Badge>;
      case 'pending':
        return <Badge variant="warning">Pending</Badge>;
      case 'sold':
        return <Badge variant="info">Sold</Badge>;
      case 'withdrawn':
        return <Badge variant="error">Withdrawn</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
    }
  };

  if (!isAuthenticated) {
    router.push('/');
    return null;
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 md:ml-64 p-4 md:p-8">
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-orbitron font-bold text-transparent bg-clip-text bg-gradient-neon mb-2">
                Properties
              </h1>
              <p className="text-gray-400">Manage your real estate properties</p>
            </div>
            <Button variant="primary" onClick={() => setIsCreating(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Property
            </Button>
          </div>

          {/* Filters */}
          <Card className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search by address, city, MLS ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  icon={<Search className="w-5 h-5 text-gray-400" />}
                />
              </div>
              <Select
                options={[
                  { value: 'all', label: 'All Statuses' },
                  { value: 'active', label: 'Active' },
                  { value: 'pending', label: 'Pending' },
                  { value: 'sold', label: 'Sold' },
                  { value: 'withdrawn', label: 'Withdrawn' },
                ]}
                value={statusFilter}
                onChange={(value) => setStatusFilter(value)}
                placeholder="Filter by status"
              />
            </div>
          </Card>

          {/* Properties Grid */}
          {isLoading ? (
            <Card className="p-12 text-center">
              <div className="text-gray-400">Loading properties...</div>
            </Card>
          ) : filteredProperties.length === 0 ? (
            <Card className="p-12 text-center">
              <Home className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">No properties found</p>
              <p className="text-sm text-gray-500 mt-2">
                {searchQuery ? 'Try adjusting your search' : 'Add your first property to get started'}
              </p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredProperties.map((property: Property) => (
                <motion.div
                  key={property.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Card className="p-6 hover:border-neon-cyan transition-colors cursor-pointer"
                    onClick={() => {
                      setSelectedProperty(property);
                      setFormData({
                        address: property.address,
                        city: property.city || '',
                        state: property.state || '',
                        zip_code: property.zip_code || '',
                        mls_id: property.mls_id || '',
                        property_type: property.property_type || '',
                        list_price: property.list_price?.toString() || '',
                        transaction_type: property.transaction_type || '',
                      });
                    }}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Home className="w-5 h-5 text-neon-cyan" />
                          <h3 className="font-semibold text-white">{property.address}</h3>
                        </div>
                        {property.city && property.state && (
                          <div className="flex items-center gap-1 text-sm text-gray-400 mb-2">
                            <MapPin className="w-4 h-4" />
                            {property.city}, {property.state} {property.zip_code}
                          </div>
                        )}
                      </div>
                      {getStatusBadge(property.transaction_status)}
                    </div>

                    <div className="space-y-2 text-sm">
                      {property.property_type && (
                        <div className="flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-300">{property.property_type}</span>
                        </div>
                      )}
                      {property.list_price && (
                        <div className="flex items-center gap-2">
                          <DollarSign className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-300 font-semibold">
                            List Price: {formatPrice(property.list_price)}
                          </span>
                        </div>
                      )}
                      {property.sale_price && (
                        <div className="flex items-center gap-2">
                          <DollarSign className="w-4 h-4 text-green-400" />
                          <span className="text-green-400 font-semibold">
                            Sale Price: {formatPrice(property.sale_price)}
                          </span>
                        </div>
                      )}
                      {property.mls_id && (
                        <div className="text-gray-400">
                          MLS ID: {property.mls_id}
                        </div>
                      )}
                      {property.transaction_type && (
                        <Badge variant="info">{property.transaction_type}</Badge>
                      )}
                    </div>

                    <div className="flex gap-2 mt-4 pt-4 border-t border-neon-cyan/20">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedProperty(property);
                          setFormData({
                            address: property.address,
                            city: property.city || '',
                            state: property.state || '',
                            zip_code: property.zip_code || '',
                            mls_id: property.mls_id || '',
                            property_type: property.property_type || '',
                            list_price: property.list_price?.toString() || '',
                            transaction_type: property.transaction_type || '',
                          });
                        }}
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteDialog({ id: property.id, address: property.address });
                        }}
                      >
                        <Trash2 className="w-4 h-4 mr-2 text-red-400" />
                        Delete
                      </Button>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}

          {/* Create/Edit Dialog */}
          {(isCreating || selectedProperty) && (
            <Dialog
              isOpen={isCreating || !!selectedProperty}
              onClose={() => {
                setIsCreating(false);
                setSelectedProperty(null);
                resetForm();
              }}
              title={isCreating ? 'Add Property' : 'Edit Property'}
              size="lg"
            >
              <div className="space-y-4">
                <Input
                  label="Address *"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="123 Main St"
                  required
                />
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="City"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    placeholder="City"
                  />
                  <Input
                    label="State"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    placeholder="State"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="ZIP Code"
                    value={formData.zip_code}
                    onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })}
                    placeholder="12345"
                  />
                  <Input
                    label="MLS ID"
                    value={formData.mls_id}
                    onChange={(e) => setFormData({ ...formData, mls_id: e.target.value })}
                    placeholder="MLS123456"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Select
                    label="Property Type"
                    options={[
                      { value: '', label: 'Select type...' },
                      { value: 'single_family', label: 'Single Family' },
                      { value: 'condo', label: 'Condo' },
                      { value: 'townhouse', label: 'Townhouse' },
                      { value: 'multi_family', label: 'Multi-Family' },
                      { value: 'land', label: 'Land' },
                      { value: 'commercial', label: 'Commercial' },
                    ]}
                    value={formData.property_type}
                    onChange={(value) => setFormData({ ...formData, property_type: value })}
                    placeholder="Property type"
                  />
                  <Select
                    label="Transaction Type"
                    options={[
                      { value: '', label: 'Select type...' },
                      { value: 'sale', label: 'Sale' },
                      { value: 'rent', label: 'Rent' },
                      { value: 'lease', label: 'Lease' },
                    ]}
                    value={formData.transaction_type}
                    onChange={(value) => setFormData({ ...formData, transaction_type: value })}
                    placeholder="Transaction type"
                  />
                </div>
                <Input
                  label="List Price"
                  type="number"
                  value={formData.list_price}
                  onChange={(e) => setFormData({ ...formData, list_price: e.target.value })}
                  placeholder="0.00"
                />
                <div className="flex gap-4 justify-end pt-4 border-t border-neon-cyan/20">
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setIsCreating(false);
                      setSelectedProperty(null);
                      resetForm();
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={isCreating ? handleCreate : handleUpdate}
                    disabled={createMutation.isPending || updateMutation.isPending}
                  >
                    {isCreating ? 'Create' : 'Update'}
                  </Button>
                </div>
              </div>
            </Dialog>
          )}

          {/* Delete Confirmation */}
          {deleteDialog && (
            <ConfirmationDialog
              isOpen={!!deleteDialog}
              onClose={() => setDeleteDialog(null)}
              onConfirm={() => {
                // Note: Backend doesn't have delete endpoint, so we'll just show a message
                toast.error('Delete functionality not available in backend');
                setDeleteDialog(null);
              }}
              title="Delete Property"
              message={`Are you sure you want to delete "${deleteDialog.address}"? This action cannot be undone.`}
              confirmText="Delete"
              cancelText="Cancel"
              variant="danger"
            />
          )}
        </motion.div>
      </div>
    </div>
  );
}

