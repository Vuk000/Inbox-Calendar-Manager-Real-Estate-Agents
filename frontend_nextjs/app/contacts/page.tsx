'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input, Textarea } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar } from '@/components/ui/avatar';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { contactAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { Plus, Search, Mail, Phone, MapPin, Edit, Trash2, User, Building } from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { Dialog } from '@/components/ui/drawer';
import { toast } from 'react-hot-toast';
import { Select } from '@/components/ui/select';
import { Table } from '@/components/ui/table';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

interface Contact {
  id: number;
  first_name: string;
  last_name?: string;
  full_name?: string;
  email?: string;
  phone?: string;
  phone_number?: string;
  company?: string;
  address?: string;
  address_line1?: string;
  notes?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export default function ContactsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');

  const { data: contacts, isLoading, refetch } = useAPI(
    ['contacts', searchQuery],
    () => contactAPI.listContacts({ search: searchQuery || undefined }),
    { enabled: isAuthenticated }
  );

  const createContactMutation = useAPIMutation(
    (contact: Partial<Contact>) => contactAPI.createContact(contact),
    {
      onSuccess: () => {
        toast.success('Contact created successfully');
        setIsCreating(false);
        refetch();
      },
    }
  );

  const updateContactMutation = useAPIMutation(
    ({ id, updates }: { id: number; updates: Partial<Contact> }) => contactAPI.updateContact(id, updates),
    {
      onSuccess: () => {
        toast.success('Contact updated successfully');
        setIsEditing(false);
        setSelectedContact(null);
        refetch();
      },
    }
  );

  const deleteContactMutation = useAPIMutation(
    (id: number) => contactAPI.deleteContact(id),
    {
      onSuccess: () => {
        toast.success('Contact deleted');
        setSelectedContact(null);
        refetch();
      },
    }
  );

  const filteredContacts = useMemo(() => {
    const contactList = contacts || [];
    if (!searchQuery) return contactList;
    return contactList.filter((contact: Contact) => {
      const fullName = contact.full_name || `${contact.first_name} ${contact.last_name || ''}`.trim();
      const email = contact.email || '';
      const phone = contact.phone || contact.phone_number || '';
      const company = contact.company || '';
      return (
        fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        phone.includes(searchQuery) ||
        company.toLowerCase().includes(searchQuery.toLowerCase())
      );
    });
  }, [contacts, searchQuery]);

  const handleCreateContact = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    createContactMutation.mutate({
      first_name: formData.get('full_name') as string,
      email: formData.get('email') as string || undefined,
      phone: formData.get('phone_number') as string || undefined,
      company: formData.get('company') as string || undefined,
      address_line1: formData.get('address') as string || undefined,
      notes: formData.get('notes') as string || undefined,
    });
  };

  const handleUpdateContact = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedContact) return;
    const formData = new FormData(e.currentTarget);
    updateContactMutation.mutate({
      id: selectedContact.id,
      updates: {
        first_name: formData.get('full_name') as string,
        email: formData.get('email') as string || undefined,
        phone: formData.get('phone_number') as string || undefined,
        company: formData.get('company') as string || undefined,
        address_line1: formData.get('address') as string || undefined,
        notes: formData.get('notes') as string || undefined,
      },
    });
  };

  const handleDelete = () => {
    if (!selectedContact) return;
    if (confirm(`Are you sure you want to delete ${selectedContact.full_name}?`)) {
      deleteContactMutation.mutate(selectedContact.id);
    }
  };

  const tableColumns = [
    {
      key: 'full_name' as keyof Contact,
      header: 'Name',
      render: (contact: Contact) => {
        const fullName = contact.full_name || `${contact.first_name} ${contact.last_name || ''}`.trim();
        return (
          <div className="flex items-center gap-3">
            <Avatar fallback={fullName.substring(0, 2)} />
            <span className="font-medium text-white">{fullName}</span>
          </div>
        );
      },
      sortable: true,
    },
    {
      key: 'email' as keyof Contact,
      header: 'Email',
      render: (contact: Contact) => contact.email || '-',
      sortable: true,
    },
    {
      key: 'phone' as keyof Contact,
      header: 'Phone',
      render: (contact: Contact) => contact.phone || contact.phone_number || '-',
      sortable: true,
    },
    {
      key: 'company' as keyof Contact,
      header: 'Company',
      render: (contact: Contact) => contact.company || '-',
      sortable: true,
    },
    {
      key: 'actions' as keyof Contact,
      header: 'Actions',
      render: (contact: Contact) => (
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedContact(contact);
              setIsEditing(true);
            }}
          >
            <Edit className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              if (confirm(`Delete ${contact.full_name || contact.first_name}?`)) {
                deleteContactMutation.mutate(contact.id);
              }
            }}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      ),
      sortable: false,
    },
  ];

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
                Contacts
              </h1>
              <p className="text-gray-400">Manage your contacts and leads</p>
            </div>
            <Button variant="primary" onClick={() => setIsCreating(true)}>
              <Plus className="w-4 h-4 mr-2" />
              New Contact
            </Button>
          </div>

          {/* Search */}
          <Card className="p-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search contacts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant={viewMode === 'table' ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('table')}
                >
                  Table
                </Button>
                <Button
                  variant={viewMode === 'grid' ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                >
                  Grid
                </Button>
              </div>
            </div>
          </Card>

          {/* Contacts List */}
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i} className="p-6">
                  <div className="animate-pulse space-y-4">
                    <div className="h-12 bg-gray-700 rounded"></div>
                    <div className="h-4 bg-gray-700 rounded w-2/3"></div>
                    <div className="h-4 bg-gray-700 rounded w-1/2"></div>
                  </div>
                </Card>
              ))}
            </div>
          ) : viewMode === 'table' ? (
            <Card className="p-6">
              <Table
                data={filteredContacts}
                columns={tableColumns}
                pageSize={10}
              />
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredContacts.length > 0 ? (
                filteredContacts.map((contact: Contact) => (
                  <motion.div
                    key={contact.id}
                    variants={fadeInUp}
                    whileHover={{ scale: 1.02 }}
                    onClick={() => setSelectedContact(contact)}
                  >
                    <Card
                      className={`p-6 cursor-pointer transition-colors ${
                        selectedContact?.id === contact.id
                          ? 'border-neon-cyan bg-neon-cyan/10'
                          : 'hover:border-neon-cyan'
                      }`}
                    >
                      <div className="flex items-start gap-4 mb-4">
                        <Avatar
                          size="lg"
                          fallback={(contact.full_name || `${contact.first_name} ${contact.last_name || ''}`.trim()).substring(0, 2)}
                        />
                        <div className="flex-1">
                          <h3 className="font-semibold text-white mb-1">{contact.full_name || `${contact.first_name} ${contact.last_name || ''}`.trim()}</h3>
                          {contact.company && (
                            <p className="text-sm text-gray-400 flex items-center gap-1">
                              <Building className="w-3 h-3" />
                              {contact.company}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="space-y-2">
                        {contact.email && (
                          <p className="text-sm text-gray-400 flex items-center gap-2">
                            <Mail className="w-4 h-4 text-neon-cyan" />
                            {contact.email}
                          </p>
                        )}
                        {(contact.phone || contact.phone_number) && (
                          <p className="text-sm text-gray-400 flex items-center gap-2">
                            <Phone className="w-4 h-4 text-neon-cyan" />
                            {contact.phone || contact.phone_number}
                          </p>
                        )}
                        {(contact.address || contact.address_line1) && (
                          <p className="text-sm text-gray-400 flex items-center gap-2">
                            <MapPin className="w-4 h-4 text-neon-cyan" />
                            {contact.address || contact.address_line1}
                          </p>
                        )}
                      </div>
                      {contact.tags && contact.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-neon-cyan/20">
                          {contact.tags.map((tag, index) => (
                            <Badge key={index} variant="info">{tag}</Badge>
                          ))}
                        </div>
                      )}
                    </Card>
                  </motion.div>
                ))
              ) : (
                <Card className="p-12 text-center col-span-full">
                  <User className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No contacts found</p>
                </Card>
              )}
            </div>
          )}

          {/* Create Contact Dialog */}
          <Dialog
            isOpen={isCreating}
            onClose={() => setIsCreating(false)}
            title="Create New Contact"
            size="md"
          >
            <form onSubmit={handleCreateContact} className="space-y-4">
              <Input
                name="full_name"
                label="Full Name"
                placeholder="Enter full name"
                required
              />
              <Input
                name="email"
                label="Email"
                type="email"
                placeholder="Enter email address"
              />
              <Input
                name="phone_number"
                label="Phone"
                mask="phone"
                placeholder="Enter phone number"
              />
              <Input
                name="company"
                label="Company"
                placeholder="Enter company name"
              />
              <Input
                name="address"
                label="Address"
                placeholder="Enter address"
              />
              <Textarea
                name="notes"
                label="Notes"
                placeholder="Additional notes"
              />
              <div className="flex gap-2 justify-end">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setIsCreating(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary">
                  Create Contact
                </Button>
              </div>
            </form>
          </Dialog>

          {/* Edit Contact Dialog */}
          <Dialog
            isOpen={isEditing && !!selectedContact}
            onClose={() => {
              setIsEditing(false);
              setSelectedContact(null);
            }}
            title="Edit Contact"
            size="md"
          >
            {selectedContact && (
              <form onSubmit={handleUpdateContact} className="space-y-4">
                <Input
                  name="full_name"
                  label="Full Name"
                  defaultValue={selectedContact.full_name || `${selectedContact.first_name} ${selectedContact.last_name || ''}`.trim()}
                  required
                />
                <Input
                  name="email"
                  label="Email"
                  type="email"
                  defaultValue={selectedContact.email || ''}
                />
                <Input
                  name="phone_number"
                  label="Phone"
                  mask="phone"
                  defaultValue={selectedContact.phone || selectedContact.phone_number || ''}
                />
                <Input
                  name="company"
                  label="Company"
                  defaultValue={selectedContact.company || ''}
                />
                <Input
                  name="address"
                  label="Address"
                  defaultValue={selectedContact.address || selectedContact.address_line1 || ''}
                />
                <Textarea
                  name="notes"
                  label="Notes"
                  defaultValue={selectedContact.notes || ''}
                />
                <div className="flex gap-2 justify-end">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => {
                      setIsEditing(false);
                      setSelectedContact(null);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" variant="primary">
                    Save Changes
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={handleDelete}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete
                  </Button>
                </div>
              </form>
            )}
          </Dialog>

          {/* Contact Details Sidebar */}
          {selectedContact && !isEditing && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="fixed right-0 top-0 h-full w-96 bg-dark-purple border-l border-neon-cyan/50 shadow-neon-cyan z-40 overflow-y-auto"
            >
              <Card className="p-6 m-4 border-0">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-orbitron text-neon-cyan">Contact Details</h2>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedContact(null)}
                  >
                    ×
                  </Button>
                </div>
                <div className="space-y-6">
                  <div className="flex flex-col items-center">
                    <Avatar
                      size="lg"
                      fallback={(selectedContact.full_name || `${selectedContact.first_name} ${selectedContact.last_name || ''}`.trim()).substring(0, 2)}
                      className="mb-4"
                    />
                    <h3 className="text-xl font-bold text-white mb-1">{selectedContact.full_name || `${selectedContact.first_name} ${selectedContact.last_name || ''}`.trim()}</h3>
                    {selectedContact.company && (
                      <p className="text-gray-400">{selectedContact.company}</p>
                    )}
                  </div>
                  <div className="space-y-4">
                    {selectedContact.email && (
                      <div>
                        <p className="text-sm text-gray-400 mb-1">Email</p>
                        <a
                          href={`mailto:${selectedContact.email}`}
                          className="text-neon-cyan hover:underline flex items-center gap-2"
                        >
                          <Mail className="w-4 h-4" />
                          {selectedContact.email}
                        </a>
                      </div>
                    )}
                    {(selectedContact.phone || selectedContact.phone_number) && (
                      <div>
                        <p className="text-sm text-gray-400 mb-1">Phone</p>
                        <a
                          href={`tel:${selectedContact.phone || selectedContact.phone_number}`}
                          className="text-neon-cyan hover:underline flex items-center gap-2"
                        >
                          <Phone className="w-4 h-4" />
                          {selectedContact.phone || selectedContact.phone_number}
                        </a>
                      </div>
                    )}
                    {(selectedContact.address || selectedContact.address_line1) && (
                      <div>
                        <p className="text-sm text-gray-400 mb-1">Address</p>
                        <p className="text-white flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-neon-cyan" />
                          {selectedContact.address || selectedContact.address_line1}
                        </p>
                      </div>
                    )}
                    {selectedContact.notes && (
                      <div>
                        <p className="text-sm text-gray-400 mb-1">Notes</p>
                        <p className="text-white">{selectedContact.notes}</p>
                      </div>
                    )}
                    {selectedContact.tags && selectedContact.tags.length > 0 && (
                      <div>
                        <p className="text-sm text-gray-400 mb-2">Tags</p>
                        <div className="flex flex-wrap gap-2">
                          {selectedContact.tags.map((tag, index) => (
                            <Badge key={index} variant="info">{tag}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="pt-4 border-t border-neon-cyan/20">
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        className="flex-1"
                        onClick={() => {
                          setIsEditing(true);
                        }}
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Edit
                      </Button>
                  <Button
                    variant="ghost"
                    className="text-red-400 hover:text-red-300"
                    onClick={() => {
                      if (confirm(`Delete ${selectedContact.full_name || selectedContact.first_name}?`)) {
                        deleteContactMutation.mutate(selectedContact.id);
                      }
                    }}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
}

