'use client';

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input, Textarea } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { draftAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { FileText, Plus, Save, Send, Trash2, Edit, Sparkles, CheckCircle, XCircle } from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { Dialog } from '@/components/ui/drawer';
import { toast } from 'react-hot-toast';
import { Select } from '@/components/ui/select';
import dynamic from 'next/dynamic';
import { Skeleton } from '@/components/ui/skeleton';

// Dynamically import ReactQuill to avoid SSR issues
const ReactQuill = dynamic(() => import('react-quill'), { ssr: false });
import 'react-quill/dist/quill.snow.css';

interface Draft {
  id: number;
  communication_log_id: number;
  subject: string;
  content: string;
  variant_number?: number;
  confidence_score?: number;
  approval_status: string;
  generated_at: string;
}

export default function DraftsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [selectedDraft, setSelectedDraft] = useState<Draft | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [content, setContent] = useState('');
  const [subject, setSubject] = useState('');
  const [communicationLogId, setCommunicationLogId] = useState<number | null>(null);

  const { data: drafts, isLoading, refetch } = useAPI(
    ['drafts', filterStatus, searchQuery],
    () => draftAPI.listDrafts({ status: filterStatus !== 'all' ? filterStatus : undefined }),
    { enabled: isAuthenticated }
  );

  const updateDraftMutation = useAPIMutation(
    ({ id, content }: { id: number; content: string }) => draftAPI.updateDraft(id, content),
    {
      onSuccess: () => {
        toast.success('Draft saved successfully');
        setIsEditing(false);
        refetch();
      },
    }
  );

  const deleteDraftMutation = useAPIMutation(
    (id: number) => draftAPI.deleteDraft?.(id) || Promise.resolve(),
    {
      onSuccess: () => {
        toast.success('Draft deleted');
        setSelectedDraft(null);
        refetch();
      },
    }
  );

  const sendDraftMutation = useAPIMutation(
    (id: number) => draftAPI.sendDraft(id),
    {
      onSuccess: () => {
        toast.success('Draft sent successfully');
        setSelectedDraft(null);
        refetch();
      },
    }
  );

  const filteredDrafts = useMemo(() => {
    const draftList = drafts || [];
    if (!searchQuery) return draftList;
    return draftList.filter((draft: Draft) =>
      draft.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      draft.content.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [drafts, searchQuery]);

  const handleSelectDraft = (draft: Draft) => {
    setSelectedDraft(draft);
    setContent(draft.content);
    setSubject(draft.subject);
    setIsEditing(false);
  };

  const handleSave = () => {
    if (!selectedDraft) return;
    updateDraftMutation.mutate({ id: selectedDraft.id, content });
  };

  const handleDelete = () => {
    if (!selectedDraft) return;
    if (confirm('Are you sure you want to delete this draft?')) {
      deleteDraftMutation.mutate(selectedDraft.id);
    }
  };

  const handleCreateNew = () => {
    setIsCreating(true);
    setSelectedDraft(null);
    setContent('');
    setSubject('');
    setCommunicationLogId(null);
  };

  const handleCreateDraft = async () => {
    if (!subject || !content) {
      toast.error('Subject and content are required');
      return;
    }
    // For now, we'll create a draft by updating an existing one or creating via API
    toast.info('Draft creation will be implemented');
    setIsCreating(false);
  };

  const quillModules = {
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ list: 'ordered' }, { list: 'bullet' }],
      [{ color: [] }, { background: [] }],
      ['link', 'image'],
      ['clean'],
    ],
  };

  const quillFormats = [
    'header',
    'bold',
    'italic',
    'underline',
    'strike',
    'list',
    'bullet',
    'color',
    'background',
    'link',
    'image',
  ];

  useEffect(() => {
    if (selectedDraft && !isEditing) {
      setContent(selectedDraft.content);
      setSubject(selectedDraft.subject);
    }
  }, [selectedDraft, isEditing]);

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
                Drafts
              </h1>
              <p className="text-gray-400">AI-powered email draft management</p>
            </div>
            <Button variant="primary" onClick={handleCreateNew}>
              <Plus className="w-4 h-4 mr-2" />
              New Draft
            </Button>
          </div>

          {/* Search and Filters */}
          <Card className="p-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search drafts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select
                options={[
                  { value: 'all', label: 'All Status' },
                  { value: 'pending', label: 'Pending' },
                  { value: 'approved', label: 'Approved' },
                  { value: 'rejected', label: 'Rejected' },
                ]}
                value={filterStatus}
                onChange={(value) => setFilterStatus(value)}
                placeholder="Filter by status"
                className="w-48"
              />
            </div>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Draft List */}
            <div className="lg:col-span-1 space-y-2">
              {isLoading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-24" />
                  ))}
                </div>
              ) : filteredDrafts.length > 0 ? (
                filteredDrafts.map((draft: Draft) => (
                  <motion.div
                    key={draft.id}
                    variants={fadeInUp}
                    whileHover={{ scale: 1.02 }}
                    onClick={() => handleSelectDraft(draft)}
                  >
                    <Card
                      className={`p-4 cursor-pointer transition-colors ${
                        selectedDraft?.id === draft.id
                          ? 'border-neon-cyan bg-neon-cyan/10'
                          : 'hover:border-neon-cyan'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <h3 className="font-semibold text-white mb-1 line-clamp-1">
                            {draft.subject || '(No subject)'}
                          </h3>
                          <p className="text-sm text-gray-400 line-clamp-2 mb-2">
                            {draft.content.replace(/<[^>]*>/g, '').substring(0, 100)}...
                          </p>
                        </div>
                        {draft.variant_number && (
                          <Badge variant="info">V{draft.variant_number}</Badge>
                        )}
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={
                              draft.approval_status === 'approved'
                                ? 'success'
                                : draft.approval_status === 'rejected'
                                ? 'error'
                                : 'warning'
                            }
                          >
                            {draft.approval_status}
                          </Badge>
                          {draft.confidence_score && (
                            <Badge variant="info">
                              {Math.round(draft.confidence_score * 100)}% confidence
                            </Badge>
                          )}
                        </div>
                        <span className="text-xs text-gray-500">
                          {new Date(draft.generated_at).toLocaleDateString()}
                        </span>
                      </div>
                    </Card>
                  </motion.div>
                ))
              ) : (
                <Card className="p-12 text-center">
                  <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No drafts found</p>
                </Card>
              )}
            </div>

            {/* Draft Editor */}
            <div className="lg:col-span-2">
              <AnimatePresence>
                {(selectedDraft || isCreating) && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                  >
                    <Card className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                          {selectedDraft?.variant_number && (
                            <Badge variant="info">
                              <Sparkles className="w-3 h-3 mr-1" />
                              AI Variant {selectedDraft.variant_number}
                            </Badge>
                          )}
                          {selectedDraft?.confidence_score && (
                            <Badge variant="info">
                              {Math.round(selectedDraft.confidence_score * 100)}% Confidence
                            </Badge>
                          )}
                        </div>
                        <div className="flex gap-2">
                          {selectedDraft && !isEditing && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setIsEditing(true)}
                              >
                                <Edit className="w-4 h-4 mr-2" />
                                Edit
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={handleDelete}
                              >
                                <Trash2 className="w-4 h-4 mr-2" />
                                Delete
                              </Button>
                            </>
                          )}
                          {isEditing && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setIsEditing(false);
                                  if (selectedDraft) {
                                    setContent(selectedDraft.content);
                                    setSubject(selectedDraft.subject);
                                  }
                                }}
                              >
                                Cancel
                              </Button>
                              <Button
                                variant="secondary"
                                size="sm"
                                onClick={handleSave}
                                disabled={updateDraftMutation.isPending}
                              >
                                <Save className="w-4 h-4 mr-2" />
                                Save
                              </Button>
                            </>
                          )}
                          {isCreating && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setIsCreating(false)}
                              >
                                Cancel
                              </Button>
                              <Button
                                variant="secondary"
                                size="sm"
                                onClick={handleCreateDraft}
                              >
                                <Save className="w-4 h-4 mr-2" />
                                Save Draft
                              </Button>
                            </>
                          )}
                          {selectedDraft && selectedDraft.approval_status === 'approved' && (
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => sendDraftMutation.mutate(selectedDraft.id)}
                              disabled={sendDraftMutation.isPending}
                            >
                              <Send className="w-4 h-4 mr-2" />
                              Send
                            </Button>
                          )}
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div>
                          <Input
                            label="Subject"
                            value={subject}
                            onChange={(e) => setSubject(e.target.value)}
                            disabled={!isEditing && !isCreating}
                            placeholder="Email subject"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-neon-cyan mb-2">
                            Content
                          </label>
                          {typeof window !== 'undefined' && (
                            <div className="bg-dark-purple/50 border border-neon-cyan/30 rounded-lg overflow-hidden">
                              <style jsx global>{`
                                .quill {
                                  background: transparent;
                                }
                                .ql-container {
                  font-family: var(--font-inter), sans-serif;
                  color: #ffffff;
                  font-size: 14px;
                  min-height: 300px;
                }
                .ql-editor {
                  color: #ffffff;
                }
                .ql-editor.ql-blank::before {
                  color: #6b7280;
                }
                .ql-toolbar {
                  background: rgba(26, 0, 51, 0.5);
                  border-bottom: 1px solid rgba(0, 255, 255, 0.3);
                }
                .ql-toolbar .ql-stroke {
                  stroke: #00FFFF;
                }
                .ql-toolbar .ql-fill {
                  fill: #00FFFF;
                }
                .ql-toolbar button:hover,
                .ql-toolbar button.ql-active {
                  background: rgba(0, 255, 255, 0.2);
                }
                .ql-container {
                  border: none;
                }
                              `}</style>
                              <ReactQuill
                                theme="snow"
                                value={content}
                                onChange={setContent}
                                modules={quillModules}
                                formats={quillFormats}
                                readOnly={!isEditing && !isCreating}
                                placeholder="Write your email draft..."
                              />
                            </div>
                          )}
                        </div>

                        {selectedDraft && (
                          <div className="pt-4 border-t border-neon-cyan/20">
                            <div className="text-sm text-gray-400">
                              <p>Generated: {new Date(selectedDraft.generated_at).toLocaleString()}</p>
                              <p>Status: {selectedDraft.approval_status}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    </Card>
                  </motion.div>
                )}
              </AnimatePresence>

              {!selectedDraft && !isCreating && (
                <Card className="p-12 text-center">
                  <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-2">Select a draft to view or edit</p>
                  <Button variant="secondary" onClick={handleCreateNew}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create New Draft
                  </Button>
                </Card>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

