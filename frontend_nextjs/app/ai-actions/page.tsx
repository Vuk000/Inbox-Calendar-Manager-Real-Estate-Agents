'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { aiActionsAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { 
  Sparkles, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertCircle,
  Filter,
  Eye
} from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { toast } from 'react-hot-toast';
import { Dialog } from '@/components/ui/drawer';
import { Textarea } from '@/components/ui/input';
import { Select } from '@/components/ui/select';

interface AIAction {
  id: number;
  action_type: string;
  status: string;
  proposed_data: Record<string, any>;
  reason: string;
  confidence_score?: number | null;
  result_data?: Record<string, any> | null;
  error_message?: string | null;
  expires_at: string;
  created_at: string;
  confirmed_at?: string | null;
  executed_at?: string | null;
}

export default function AIActionsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const [selectedAction, setSelectedAction] = useState<AIAction | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [confirmNotes, setConfirmNotes] = useState('');

  const { data: aiActionsData, isLoading, refetch } = useAPI(
    ['ai-actions', statusFilter],
    () => aiActionsAPI.listAIActions({ 
      status_filter: statusFilter === 'all' ? undefined : statusFilter,
      limit: 50,
    }),
    { enabled: isAuthenticated }
  );

  const confirmMutation = useAPIMutation(
    ({ id, notes }: { id: number; notes?: string }) => aiActionsAPI.confirmAction(id, notes),
    {
      onSuccess: () => {
        toast.success('Action confirmed');
        setSelectedAction(null);
        setConfirmNotes('');
        refetch();
      },
      onError: () => {
        toast.error('Failed to confirm action');
      },
    }
  );

  const rejectMutation = useAPIMutation(
    ({ id, reason }: { id: number; reason: string }) => aiActionsAPI.rejectAction(id, reason),
    {
      onSuccess: () => {
        toast.success('Action rejected');
        setSelectedAction(null);
        setRejectReason('');
        refetch();
      },
      onError: () => {
        toast.error('Failed to reject action');
      },
    }
  );

  const actions = aiActionsData?.actions || [];

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return <Badge variant="warning">Pending</Badge>;
      case 'confirmed':
        return <Badge variant="success">Confirmed</Badge>;
      case 'rejected':
        return <Badge variant="error">Rejected</Badge>;
      case 'expired':
        return <Badge variant="default">Expired</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
    }
  };

  const getActionTypeIcon = (actionType: string) => {
    switch (actionType.toLowerCase()) {
      case 'contact_merge':
        return '👥';
      case 'draft_generation':
        return '✍️';
      case 'task_creation':
        return '✅';
      case 'email_send':
        return '📧';
      default:
        return '🤖';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
    });
  };

  const handleConfirm = () => {
    if (!selectedAction) return;
    confirmMutation.mutate({ id: selectedAction.id, notes: confirmNotes || undefined });
  };

  const handleReject = () => {
    if (!selectedAction || !rejectReason.trim()) {
      toast.error('Please provide a reason for rejection');
      return;
    }
    rejectMutation.mutate({ id: selectedAction.id, reason: rejectReason });
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
                AI Actions
              </h1>
              <p className="text-gray-400">Review and approve AI-suggested actions</p>
            </div>
            <Select
              options={[
                { value: 'all', label: 'All Actions' },
                { value: 'pending', label: 'Pending' },
                { value: 'confirmed', label: 'Confirmed' },
                { value: 'rejected', label: 'Rejected' },
                { value: 'expired', label: 'Expired' },
              ]}
              value={statusFilter}
              onChange={(value) => setStatusFilter(value)}
              placeholder="Filter by status"
            />
          </div>

          {isLoading ? (
            <Card className="p-12 text-center">
              <div className="text-gray-400">Loading AI actions...</div>
            </Card>
          ) : actions.length === 0 ? (
            <Card className="p-12 text-center">
              <Sparkles className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">No AI actions found</p>
              <p className="text-sm text-gray-500 mt-2">
                {statusFilter === 'pending' 
                  ? 'All actions have been reviewed' 
                  : 'No actions match this filter'}
              </p>
            </Card>
          ) : (
            <div className="space-y-4">
              {actions.map((action: AIAction) => (
                <motion.div
                  key={action.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Card className="p-6 hover:border-neon-cyan transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <span className="text-2xl">{getActionTypeIcon(action.action_type)}</span>
                          <div>
                            <h3 className="font-semibold text-white capitalize">
                              {action.action_type.replace(/_/g, ' ')}
                            </h3>
                            <p className="text-sm text-gray-400">{action.reason}</p>
                          </div>
                          {getStatusBadge(action.status)}
                          {action.confidence_score !== null && action.confidence_score !== undefined && (
                            <Badge variant="info">
                              {Math.round(action.confidence_score * 100)}% confidence
                            </Badge>
                          )}
                        </div>

                        <div className="bg-dark-purple/50 rounded-lg p-4 mb-3">
                          <h4 className="text-sm font-medium text-neon-cyan mb-2">Proposed Data:</h4>
                          <pre className="text-xs text-gray-300 overflow-x-auto">
                            {JSON.stringify(action.proposed_data, null, 2)}
                          </pre>
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            Created: {formatDate(action.created_at)}
                          </span>
                          {action.expires_at && (
                            <span className="flex items-center gap-1">
                              <AlertCircle className="w-4 h-4" />
                              Expires: {formatDate(action.expires_at)}
                            </span>
                          )}
                        </div>

                        {action.result_data && (
                          <div className="mt-3 bg-green-500/10 border border-green-500/20 rounded-lg p-3">
                            <h4 className="text-sm font-medium text-green-400 mb-1">Result:</h4>
                            <pre className="text-xs text-gray-300 overflow-x-auto">
                              {JSON.stringify(action.result_data, null, 2)}
                            </pre>
                          </div>
                        )}

                        {action.error_message && (
                          <div className="mt-3 bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                            <h4 className="text-sm font-medium text-red-400 mb-1">Error:</h4>
                            <p className="text-xs text-gray-300">{action.error_message}</p>
                          </div>
                        )}
                      </div>

                      <div className="flex flex-col gap-2 ml-4">
                        {action.status === 'pending' && (
                          <>
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => setSelectedAction(action)}
                            >
                              <Eye className="w-4 h-4 mr-2" />
                              Review
                            </Button>
                          </>
                        )}
                        {action.status === 'confirmed' && action.confirmed_at && (
                          <div className="text-xs text-gray-400">
                            Confirmed: {formatDate(action.confirmed_at)}
                          </div>
                        )}
                        {action.status === 'rejected' && (
                          <div className="text-xs text-gray-400">
                            Rejected
                          </div>
                        )}
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}

          {/* Review Dialog */}
          {selectedAction && (
            <Dialog
              isOpen={!!selectedAction}
              onClose={() => {
                setSelectedAction(null);
                setRejectReason('');
                setConfirmNotes('');
              }}
              title={`Review ${selectedAction.action_type.replace(/_/g, ' ')}`}
              size="lg"
            >
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-neon-cyan mb-2">Reason:</h4>
                  <p className="text-gray-300">{selectedAction.reason}</p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-neon-cyan mb-2">Proposed Data:</h4>
                  <div className="bg-dark-purple/50 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-xs text-gray-300">
                      {JSON.stringify(selectedAction.proposed_data, null, 2)}
                    </pre>
                  </div>
                </div>

                {selectedAction.confidence_score !== null && selectedAction.confidence_score !== undefined && (
                  <div>
                    <h4 className="text-sm font-medium text-neon-cyan mb-2">Confidence Score:</h4>
                    <Badge variant="info">{Math.round(selectedAction.confidence_score * 100)}%</Badge>
                  </div>
                )}

                <div>
                  <h4 className="text-sm font-medium text-neon-cyan mb-2">Confirmation Notes (Optional):</h4>
                  <Textarea
                    value={confirmNotes}
                    onChange={(e) => setConfirmNotes(e.target.value)}
                    placeholder="Add any notes about this action..."
                    rows={3}
                  />
                </div>

                <div>
                  <h4 className="text-sm font-medium text-red-400 mb-2">Rejection Reason (Required if rejecting):</h4>
                  <Textarea
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                    placeholder="Explain why you're rejecting this action..."
                    rows={3}
                  />
                </div>

                <div className="flex gap-4 justify-end pt-4 border-t border-neon-cyan/20">
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setSelectedAction(null);
                      setRejectReason('');
                      setConfirmNotes('');
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="error"
                    onClick={handleReject}
                    disabled={!rejectReason.trim() || rejectMutation.isPending}
                  >
                    <XCircle className="w-4 h-4 mr-2" />
                    Reject
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleConfirm}
                    disabled={confirmMutation.isPending}
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Confirm
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

