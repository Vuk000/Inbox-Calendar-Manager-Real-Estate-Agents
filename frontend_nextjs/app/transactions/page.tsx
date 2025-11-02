'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { HolographicCard } from '@/components/cyberpunk/HolographicCard';
import { ScrollReveal } from '@/components/cyberpunk/ScrollReveal';
import { NeonText } from '@/components/cyberpunk/NeonText';
import { NeonButton } from '@/components/cyberpunk/NeonButton';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input, Textarea } from '@/components/ui/input';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { transactionAPI, contactAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { 
  Plus, 
  Search, 
  Filter,
  Edit,
  Trash2,
  DollarSign,
  Calendar,
  User,
  Home,
  TrendingUp
} from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { toast } from 'react-hot-toast';
import { Dialog } from '@/components/ui/drawer';
import { ConfirmationDialog } from '@/components/ui/drawer';
import { Select } from '@/components/ui/select';
import { DndContext, DragEndEvent, DragOverlay, DragStartEvent, closestCorners, useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface Transaction {
  id: number;
  title: string;
  description?: string | null;
  transaction_type: string;
  stage: string;
  contact_id: number;
  property_id?: number | null;
  estimated_value?: number | null;
  commission_percentage?: number | null;
  estimated_commission?: number | null;
  probability: number;
  lead_date?: string | null;
  contract_date?: string | null;
  closing_date?: string | null;
  created_at: string;
}

const STAGES = [
  { id: 'lead', label: 'Lead', color: 'neon-cyan' },
  { id: 'active', label: 'Active', color: 'neon-pink' },
  { id: 'pending', label: 'Pending', color: 'yellow-400' },
  { id: 'under_contract', label: 'Under Contract', color: 'blue-400' },
  { id: 'closed_won', label: 'Closed Won', color: 'green-400' },
  { id: 'closed_lost', label: 'Closed Lost', color: 'red-400' },
  { id: 'archived', label: 'Archived', color: 'gray-400' },
];

function TransactionCard({ transaction, onEdit, onDelete }: { 
  transaction: Transaction; 
  onEdit: (t: Transaction) => void;
  onDelete: (id: number) => void;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: transaction.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const stageColor = STAGES.find(s => s.id === transaction.stage)?.color || 'gray-400';

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <Card className="p-4 mb-3 cursor-move hover:border-neon-cyan transition-colors">
        <div className="flex items-start justify-between mb-2">
          <h4 className="font-semibold text-white">{transaction.title}</h4>
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onEdit(transaction);
              }}
            >
              <Edit className="w-3 h-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(transaction.id);
              }}
            >
              <Trash2 className="w-3 h-3 text-red-400" />
            </Button>
          </div>
        </div>
        <div className="space-y-2 text-sm">
          <Badge variant="info">{transaction.transaction_type}</Badge>
          {transaction.estimated_value && (
            <div className="flex items-center gap-1 text-gray-400">
              <DollarSign className="w-4 h-4" />
              ${transaction.estimated_value.toLocaleString()}
            </div>
          )}
          {transaction.probability && (
            <div className="flex items-center gap-1 text-gray-400">
              <TrendingUp className="w-4 h-4" />
              {transaction.probability}% probability
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}

function DroppableColumn({ id, children }: { id: string; children: React.ReactNode }) {
  const { setNodeRef } = useDroppable({ id });
  return <div ref={setNodeRef} className="h-full">{children}</div>;
}

export default function TransactionsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [stageFilter, setStageFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [isCreating, setIsCreating] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [activeTransaction, setActiveTransaction] = useState<number | null>(null);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    transaction_type: 'buyer',
    contact_id: 0,
    property_id: 0,
    estimated_value: '',
    commission_percentage: '',
    stage: 'lead',
  });

  const { data: transactionsData, isLoading, refetch } = useAPI(
    ['transactions', stageFilter, typeFilter, searchQuery],
    () => transactionAPI.listTransactions({
      stage: stageFilter !== 'all' ? stageFilter : undefined,
      transaction_type: typeFilter !== 'all' ? typeFilter : undefined,
      search: searchQuery || undefined,
      limit: 500,
    }),
    { enabled: isAuthenticated }
  );

  const { data: contacts } = useAPI(
    ['contacts'],
    () => contactAPI.listContacts({ limit: 100 }),
    { enabled: isAuthenticated }
  );

  const { data: stats } = useAPI(
    ['transaction-stats'],
    () => transactionAPI.getPipelineStats(),
    { enabled: isAuthenticated }
  );

  const transactions = transactionsData?.transactions || [];

  const createMutation = useAPIMutation(
    (data: any) => transactionAPI.createTransaction(data),
    {
      onSuccess: () => {
        toast.success('Transaction created');
        setIsCreating(false);
        resetForm();
        refetch();
      },
      onError: (error: any) => {
        toast.error(error?.response?.data?.detail || 'Failed to create transaction');
      },
    }
  );

  const updateMutation = useAPIMutation(
    ({ id, data }: { id: number; data: any }) => transactionAPI.updateTransaction(id, data),
    {
      onSuccess: () => {
        toast.success('Transaction updated');
        setSelectedTransaction(null);
        resetForm();
        refetch();
      },
    }
  );

  const updateStageMutation = useAPIMutation(
    ({ id, stage }: { id: number; stage: string }) => transactionAPI.updateTransactionStage(id, stage),
    {
      onSuccess: () => {
        toast.success('Transaction stage updated');
        refetch();
      },
    }
  );

  const deleteMutation = useAPIMutation(
    (id: number) => transactionAPI.deleteTransaction(id),
    {
      onSuccess: () => {
        toast.success('Transaction deleted');
        refetch();
      },
    }
  );

  const transactionsByStage = useMemo(() => {
    const grouped: Record<string, Transaction[]> = {};
    STAGES.forEach(stage => {
      grouped[stage.id] = [];
    });
    transactions.forEach((t: Transaction) => {
      if (grouped[t.stage]) {
        grouped[t.stage].push(t);
      }
    });
    return grouped;
  }, [transactions]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveTransaction(event.active.id as number);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveTransaction(null);

    if (!over) return;

    const transactionId = active.id as number;
    const newStage = over.id as string;

    const transaction = transactions.find((t: Transaction) => t.id === transactionId);
    if (transaction && transaction.stage !== newStage) {
      updateStageMutation.mutate({ id: transactionId, stage: newStage });
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      transaction_type: 'buyer',
      contact_id: 0,
      property_id: 0,
      estimated_value: '',
      commission_percentage: '',
      stage: 'lead',
    });
  };

  const handleCreate = () => {
    if (!formData.title.trim() || !formData.contact_id) {
      toast.error('Title and contact are required');
      return;
    }
    createMutation.mutate({
      title: formData.title,
      description: formData.description || undefined,
      transaction_type: formData.transaction_type,
      contact_id: formData.contact_id,
      property_id: formData.property_id || undefined,
      estimated_value: formData.estimated_value ? parseFloat(formData.estimated_value) : undefined,
      commission_percentage: formData.commission_percentage ? parseFloat(formData.commission_percentage) : undefined,
      stage: formData.stage,
    });
  };

  const handleUpdate = () => {
    if (!selectedTransaction || !formData.title.trim() || !formData.contact_id) {
      toast.error('Title and contact are required');
      return;
    }
    updateMutation.mutate({
      id: selectedTransaction.id,
      data: {
        title: formData.title,
        description: formData.description || undefined,
        transaction_type: formData.transaction_type,
        contact_id: formData.contact_id,
        property_id: formData.property_id || undefined,
        estimated_value: formData.estimated_value ? parseFloat(formData.estimated_value) : undefined,
        commission_percentage: formData.commission_percentage ? parseFloat(formData.commission_percentage) : undefined,
        stage: formData.stage,
      },
    });
  };

  if (!isAuthenticated) {
    router.push('/');
    return null;
  }

  return (
    <div className="flex min-h-screen bg-dark-bg">
      <Sidebar />
      <div className="flex-1 md:ml-64 p-4 md:p-8">
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          <ScrollReveal>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-4xl font-orbitron font-bold mb-2">
                  <NeonText color="purple">Transactions</NeonText>
                </h1>
                <p className="text-gray-400">Manage your deal pipeline</p>
              </div>
              <NeonButton onClick={() => setIsCreating(true)} glowColor="purple">
                <Plus className="w-4 h-4 mr-2" />
                New Transaction
              </NeonButton>
            </div>
          </ScrollReveal>

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="p-4">
                <div className="text-sm text-gray-400 mb-1">Total Deals</div>
                <div className="text-2xl font-bold text-neon-cyan">{stats.total || 0}</div>
              </Card>
              <Card className="p-4">
                <div className="text-sm text-gray-400 mb-1">Active</div>
                <div className="text-2xl font-bold text-neon-pink">{stats.active || 0}</div>
              </Card>
              <Card className="p-4">
                <div className="text-sm text-gray-400 mb-1">Under Contract</div>
                <div className="text-2xl font-bold text-blue-400">{stats.under_contract || 0}</div>
              </Card>
              <Card className="p-4">
                <div className="text-sm text-gray-400 mb-1">Closed Won</div>
                <div className="text-2xl font-bold text-green-400">{stats.closed_won || 0}</div>
              </Card>
            </div>
          )}

          {/* Filters */}
          <Card className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search transactions..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  icon={<Search className="w-5 h-5 text-gray-400" />}
                />
              </div>
              <Select
                options={[
                  { value: 'all', label: 'All Stages' },
                  ...STAGES.map(s => ({ value: s.id, label: s.label })),
                ]}
                value={stageFilter}
                onChange={(value) => setStageFilter(value)}
                placeholder="Filter by stage"
              />
              <Select
                options={[
                  { value: 'all', label: 'All Types' },
                  { value: 'buyer', label: 'Buyer' },
                  { value: 'seller', label: 'Seller' },
                  { value: 'both', label: 'Both' },
                  { value: 'lease', label: 'Lease' },
                  { value: 'referral', label: 'Referral' },
                ]}
                value={typeFilter}
                onChange={(value) => setTypeFilter(value)}
                placeholder="Filter by type"
              />
            </div>
          </Card>

          {/* Kanban Board */}
          {isLoading ? (
            <Card className="p-12 text-center">
              <div className="text-gray-400">Loading transactions...</div>
            </Card>
          ) : (
            <DndContext
              collisionDetection={closestCorners}
              onDragStart={handleDragStart}
              onDragEnd={handleDragEnd}
            >
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-7 gap-4 overflow-x-auto pb-4">
                {STAGES.map((stage) => {
                  const stageTransactions = transactionsByStage[stage.id] || [];
                  return (
                    <DroppableColumn key={stage.id} id={stage.id}>
                      <div className="flex-shrink-0 w-full md:w-auto">
                        <Card className="p-4 min-h-[500px]">
                          <div className={`flex items-center justify-between mb-4 pb-2 border-b-2 border-${stage.color}/50`}>
                            <h3 className="font-orbitron font-bold text-white">
                              {stage.label}
                            </h3>
                            <Badge variant="default">{stageTransactions.length}</Badge>
                          </div>
                          <SortableContext
                            items={stageTransactions.map(t => t.id)}
                            strategy={verticalListSortingStrategy}
                          >
                            <div className="space-y-2">
                              {stageTransactions.map((transaction) => (
                                <TransactionCard
                                  key={transaction.id}
                                  transaction={transaction}
                                  onEdit={(t) => {
                                    setSelectedTransaction(t);
                                    setFormData({
                                      title: t.title,
                                      description: t.description || '',
                                      transaction_type: t.transaction_type,
                                      contact_id: t.contact_id,
                                      property_id: t.property_id || 0,
                                      estimated_value: t.estimated_value?.toString() || '',
                                      commission_percentage: t.commission_percentage?.toString() || '',
                                      stage: t.stage,
                                    });
                                  }}
                                  onDelete={(id) => {
                                    if (confirm('Are you sure you want to delete this transaction?')) {
                                      deleteMutation.mutate(id);
                                    }
                                  }}
                                />
                              ))}
                            </div>
                          </SortableContext>
                          {stageTransactions.length === 0 && (
                            <div className="text-center text-gray-500 py-8 text-sm">
                              No transactions
                            </div>
                          )}
                        </Card>
                      </div>
                    </DroppableColumn>
                  );
                })}
              </div>
              <DragOverlay>
                {activeTransaction ? (
                  <div className="opacity-50">
                    <Card className="p-4">
                      <div className="font-semibold text-white">
                        {transactions.find((t: Transaction) => t.id === activeTransaction)?.title}
                      </div>
                    </Card>
                  </div>
                ) : null}
              </DragOverlay>
            </DndContext>
          )}

          {/* Create/Edit Dialog */}
          {(isCreating || selectedTransaction) && (
            <Dialog
              isOpen={isCreating || !!selectedTransaction}
              onClose={() => {
                setIsCreating(false);
                setSelectedTransaction(null);
                resetForm();
              }}
              title={isCreating ? 'Create Transaction' : 'Edit Transaction'}
              size="lg"
            >
              <div className="space-y-4">
                <Input
                  label="Title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Transaction title"
                  required
                />
                <Textarea
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Transaction description"
                  rows={3}
                />
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-neon-cyan mb-2">
                      Transaction Type
                    </label>
                    <Select
                      options={[
                        { value: 'buyer', label: 'Buyer' },
                        { value: 'seller', label: 'Seller' },
                        { value: 'both', label: 'Both' },
                        { value: 'lease', label: 'Lease' },
                        { value: 'referral', label: 'Referral' },
                      ]}
                      value={formData.transaction_type}
                      onChange={(value) => setFormData({ ...formData, transaction_type: value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neon-cyan mb-2">
                      Stage
                    </label>
                    <Select
                      options={STAGES.map(s => ({ value: s.id, label: s.label }))}
                      value={formData.stage}
                      onChange={(value) => setFormData({ ...formData, stage: value })}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neon-cyan mb-2">
                    Contact *
                  </label>
                  <Select
                    options={[
                      { value: '0', label: 'Select contact...' },
                      ...((contacts as any[]) || []).map((c: any) => ({
                        value: String(c.id),
                        label: c.full_name || c.email || `Contact #${c.id}`,
                      })),
                    ]}
                    value={String(formData.contact_id)}
                    onChange={(value) => setFormData({ ...formData, contact_id: parseInt(value) })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Estimated Value"
                    type="number"
                    value={formData.estimated_value}
                    onChange={(e) => setFormData({ ...formData, estimated_value: e.target.value })}
                    placeholder="0.00"
                  />
                  <Input
                    label="Commission %"
                    type="number"
                    value={formData.commission_percentage}
                    onChange={(e) => setFormData({ ...formData, commission_percentage: e.target.value })}
                    placeholder="0.00"
                  />
                </div>
                <div className="flex gap-4 justify-end pt-4 border-t border-neon-cyan/20">
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setIsCreating(false);
                      setSelectedTransaction(null);
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
        </motion.div>
      </div>
    </div>
  );
}

