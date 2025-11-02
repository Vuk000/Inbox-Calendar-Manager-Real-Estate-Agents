'use client';

import { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { HolographicCard } from '@/components/cyberpunk/HolographicCard';
import { ScrollReveal } from '@/components/cyberpunk/ScrollReveal';
import { NeonText } from '@/components/cyberpunk/NeonText';
import { NeonButton } from '@/components/cyberpunk/NeonButton';
import { Input, Textarea } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { emailAPI, communicationsAPI, draftAPI, taskAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { Search, Mail, Star, Archive, Trash2, Reply, Forward, CheckSquare, Square, ChevronDown, ChevronRight, Eye, MessageSquare, Sparkles, Brain, CheckCircle2 } from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { cn } from '@/lib/utils';
import toast from 'react-hot-toast';
import { Select } from '@/components/ui/select';
import { Dialog } from '@/components/ui/drawer';
import type { Email } from '@/types/backend';

export default function InboxPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [selectedEmails, setSelectedEmails] = useState<Set<number>>(new Set());
  const [expandedThreads, setExpandedThreads] = useState<Set<string>>(new Set());
  const [previewEmail, setPreviewEmail] = useState<Email | null>(null);
  const [filter, setFilter] = useState<'all' | 'starred' | 'archived'>('all');
  const [threadSummaries, setThreadSummaries] = useState<Record<string, { summary: string; key_points: string[] }>>({});
  const [loadingSummaries, setLoadingSummaries] = useState<Set<string>>(new Set());
  const [useSemanticSearch, setUseSemanticSearch] = useState(false);
  const [emailAnalysis, setEmailAnalysis] = useState<Record<number, any>>({});
  const [analyzingEmails, setAnalyzingEmails] = useState<Set<number>>(new Set());
  const [generatingDraft, setGeneratingDraft] = useState(false);
  const [generatedDrafts, setGeneratedDrafts] = useState<any[]>([]);
  const [showDraftDialog, setShowDraftDialog] = useState(false);
  const [showCreateTaskDialog, setShowCreateTaskDialog] = useState(false);
  const [taskFormData, setTaskFormData] = useState({
    title: '',
    description: '',
    task_type: 'follow_up',
    priority: 'medium',
    due_date: '',
    due_time: '',
  });

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const { data: emails, isLoading, refetch } = useAPI(
    ['emails', debouncedSearchQuery, filter, useSemanticSearch],
    async () => {
      if (debouncedSearchQuery && useSemanticSearch) {
        const result = await emailAPI.searchEmails(debouncedSearchQuery);
        return result.results || [];
      }
      return emailAPI.listEmails({ 
        search: debouncedSearchQuery || undefined,
        starred: filter === 'starred' ? true : undefined,
        archived: filter === 'archived' ? true : undefined,
      });
    },
    { enabled: isAuthenticated }
  );

  const starMutation = useAPIMutation(
    (id: number) => communicationsAPI.starCommunication(id, true),
    {
      onSuccess: () => {
        toast.success('Email starred');
        refetch();
      },
    }
  );

  const unstarMutation = useAPIMutation(
    (id: number) => communicationsAPI.starCommunication(id, false),
    {
      onSuccess: () => {
        toast.success('Email unstarred');
        refetch();
      },
    }
  );

  const archiveMutation = useAPIMutation(
    (id: number) => communicationsAPI.archiveCommunication(id, true),
    {
      onSuccess: () => {
        toast.success('Email archived');
        refetch();
        setSelectedEmails(new Set());
      },
    }
  );

  const unarchiveMutation = useAPIMutation(
    (id: number) => communicationsAPI.archiveCommunication(id, false),
    {
      onSuccess: () => {
        toast.success('Email unarchived');
        refetch();
      },
    }
  );

  const deleteMutation = useAPIMutation(
    (id: number) => communicationsAPI.deleteCommunication(id),
    {
      onSuccess: () => {
        toast.success('Email deleted');
        refetch();
        if (previewEmail?.id === id) {
          setPreviewEmail(null);
        }
      },
    }
  );

  // Group emails by thread
  const threadedEmails = useMemo(() => {
    // Backend returns array directly, not wrapped in {items: []}
    const emailList = Array.isArray(emails) ? emails : [];
    const threads = new Map<string, Email[]>();
    const standalone: Email[] = [];

    emailList.forEach((email: Email) => {
      if (email.thread_id) {
        if (!threads.has(email.thread_id)) {
          threads.set(email.thread_id, []);
        }
        threads.get(email.thread_id)!.push(email);
      } else {
        standalone.push(email);
      }
    });

    // Sort threads by most recent email
    const sortedThreads = Array.from(threads.entries()).map(([threadId, threadEmails]) => ({
      threadId,
      emails: threadEmails.sort((a, b) => 
        new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime()
      ),
    })).sort((a, b) => 
      new Date(b.emails[0].occurred_at).getTime() - new Date(a.emails[0].occurred_at).getTime()
    );

    return { threads: sortedThreads, standalone };
  }, [emails]);

  const toggleSelectEmail = (id: number) => {
    const newSelected = new Set(selectedEmails);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedEmails(newSelected);
  };

  const toggleSelectAll = () => {
    const emailList = Array.isArray(emails) ? emails : [];
    if (selectedEmails.size === emailList.length) {
      setSelectedEmails(new Set());
    } else {
      setSelectedEmails(new Set(emailList.map((e: Email) => e.id)));
    }
  };

  const handleBulkAction = async (action: 'archive' | 'delete' | 'star' | 'unstar') => {
    if (selectedEmails.size === 0) return;

    const promises = Array.from(selectedEmails).map((id) => {
      switch (action) {
        case 'archive':
          return archiveMutation.mutateAsync(id);
        case 'delete':
          return deleteMutation.mutateAsync(id);
        case 'star':
          return starMutation.mutateAsync(id);
        case 'unstar':
          return unstarMutation.mutateAsync(id);
        default:
          return Promise.resolve();
      }
    });

    await Promise.all(promises);
    toast.success(`${selectedEmails.size} emails ${action}ed`);
    setSelectedEmails(new Set());
    refetch();
  };

  const toggleThread = (threadId: string) => {
    const newExpanded = new Set(expandedThreads);
    if (newExpanded.has(threadId)) {
      newExpanded.delete(threadId);
    } else {
      newExpanded.add(threadId);
    }
    setExpandedThreads(newExpanded);
  };

  const handleSummarizeThread = async (threadId: string, threadEmails: Email[]) => {
    if (threadSummaries[threadId] || loadingSummaries.has(threadId)) return;
    
    setLoadingSummaries(prev => new Set(prev).add(threadId));
    
    try {
      const messageIds = threadEmails.map(e => e.id);
      const summary = await communicationsAPI.summarizeThread(messageIds);
      setThreadSummaries(prev => ({
        ...prev,
        [threadId]: summary,
      }));
    } catch (error) {
      toast.error('Failed to summarize thread');
    } finally {
      setLoadingSummaries(prev => {
        const newSet = new Set(prev);
        newSet.delete(threadId);
        return newSet;
      });
    }
  };

  const handleAnalyzeEmail = async (emailId: number) => {
    if (emailAnalysis[emailId] || analyzingEmails.has(emailId)) return;
    
    setAnalyzingEmails(prev => new Set(prev).add(emailId));
    
    try {
      const analysis = await emailAPI.analyzeEmail(emailId);
      setEmailAnalysis(prev => ({
        ...prev,
        [emailId]: analysis,
      }));
      toast.success('Email analyzed');
    } catch (error) {
      toast.error('Failed to analyze email');
    } finally {
      setAnalyzingEmails(prev => {
        const newSet = new Set(prev);
        newSet.delete(emailId);
        return newSet;
      });
    }
  };

  const handleGenerateDraft = async (emailId: number) => {
    if (generatingDraft) return;
    
    setGeneratingDraft(true);
    
    try {
      const drafts = await draftAPI.generateDraft(emailId, 3); // Generate 3 variants
      setGeneratedDrafts(Array.isArray(drafts) ? drafts : [drafts]);
      setShowDraftDialog(true);
      toast.success('Draft generated');
    } catch (error) {
      toast.error('Failed to generate draft');
    } finally {
      setGeneratingDraft(false);
    }
  };

  const handleCreateTaskFromEmail = () => {
    if (!previewEmail) return;
    
    // Pre-fill task form with email data
    setTaskFormData({
      title: previewEmail.subject || 'Follow up on email',
      description: previewEmail.summary || previewEmail.body || '',
      task_type: 'follow_up',
      priority: previewEmail.urgency_score && previewEmail.urgency_score > 70 ? 'high' : 'medium',
      due_date: '',
      due_time: '',
    });
    setShowCreateTaskDialog(true);
  };

  const handleSubmitTask = async () => {
    if (!previewEmail || !taskFormData.title.trim()) {
      toast.error('Task title is required');
      return;
    }

    try {
      await taskAPI.createTask({
        title: taskFormData.title,
        description: taskFormData.description || undefined,
        task_type: taskFormData.task_type,
        priority: taskFormData.priority,
        message_id: previewEmail.id, // Link to email
        due_date: taskFormData.due_date || undefined,
        due_time: taskFormData.due_time || undefined,
      });
      toast.success('Task created');
      setShowCreateTaskDialog(false);
      setTaskFormData({
        title: '',
        description: '',
        task_type: 'follow_up',
        priority: 'medium',
        due_date: '',
        due_time: '',
      });
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to create task');
    }
  };

  if (!isAuthenticated) {
    router.push('/');
    return null;
  }

  return (
    <div className="flex min-h-screen bg-dark-bg">
      <Sidebar />
      <div className={cn("flex-1 p-4 md:p-8 transition-all duration-300", {
          "md:ml-64": !previewEmail,
          "md:ml-64 md:mr-1/3": previewEmail,
        })}>
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl sm:text-4xl font-orbitron font-bold mb-2">
                <NeonText color="blue">Inbox</NeonText>
              </h1>
              <p className="text-gray-400 text-sm sm:text-base">AI-powered email management</p>
            </div>
            <div className="flex gap-2 flex-wrap">
              <Button
                variant={filter === 'all' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setFilter('all')}
              >
                All
              </Button>
              <Button
                variant={filter === 'starred' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setFilter('starred')}
              >
                Starred
              </Button>
              <Button
                variant={filter === 'archived' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setFilter('archived')}
              >
                Archived
              </Button>
            </div>
          </div>

          <HolographicCard glowColor="blue" className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search emails..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              {searchQuery && (
                <NeonButton
                  glowColor={useSemanticSearch ? 'blue' : 'purple'}
                  size="sm"
                  onClick={() => setUseSemanticSearch(!useSemanticSearch)}
                  title="Toggle semantic search"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  {useSemanticSearch ? 'Semantic' : 'Text'}
                </NeonButton>
              )}
              <div className="flex gap-2">
                <Button
                  variant={filter === 'all' ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setFilter('all')}
                >
                  All
                </Button>
                <Button
                  variant={filter === 'starred' ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setFilter('starred')}
                >
                  Starred
                </Button>
                <Button
                  variant={filter === 'archived' ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setFilter('archived')}
                >
                  Archived
                </Button>
              </div>
            </div>
            {debouncedSearchQuery && (
              <div className="mt-2 text-sm text-gray-400">
                {isLoading ? 'Searching...' : `Found ${Array.isArray(emails) ? emails.length : 0} results`}
                {useSemanticSearch && ' (semantic search)'}
              </div>
            )}
          </HolographicCard>

          {/* Bulk Actions */}
          {selectedEmails.size > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-4 p-4 bg-neon-cyan/10 rounded-lg border border-neon-cyan/20 neon-border"
            >
              <span className="text-neon-cyan font-medium">
                {selectedEmails.size} selected
              </span>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={() => handleBulkAction('archive')} className="hover:bg-neon-cyan/20">
                  <Archive className="w-4 h-4 mr-2" />
                  Archive
                </Button>
                <Button variant="ghost" size="sm" onClick={() => handleBulkAction('delete')} className="hover:bg-neon-pink/20">
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </Button>
              </div>
            </motion.div>
          )}

          {/* Email List */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Email List */}
            <div className="lg:col-span-2 space-y-2">
              {isLoading ? (
                <div className="flex justify-center py-12">
                  <div className="spinner w-12 h-12" />
                </div>
              ) : (
                <>
                  {/* Select All */}
                  <Card className="p-3">
                    <button
                      onClick={toggleSelectAll}
                      className="flex items-center gap-2 text-sm text-gray-400 hover:text-neon-cyan"
                    >
                      {selectedEmails.size === (Array.isArray(emails) ? emails : []).length ? (
                        <CheckSquare className="w-4 h-4" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                      Select All
                    </button>
                  </Card>

                  {/* Threaded Emails */}
                  {threadedEmails.threads.map(({ threadId, emails: threadEmails }) => {
                    const isExpanded = expandedThreads.has(threadId);
                    const latestEmail = threadEmails[0];
                    const isSelected = selectedEmails.has(latestEmail.id);
                    const isThreadSelected = threadEmails.some((e) => selectedEmails.has(e.id));
                    const threadSummary = threadSummaries[threadId];
                    const isSummarizing = loadingSummaries.has(threadId);

                    return (
                      <motion.div
                        key={threadId}
                        whileHover={{ x: 4, scale: 1.01 }}
                        transition={{ duration: 0.2 }}
                      >
                        <HolographicCard glowColor="blue" className="p-4 cursor-pointer">
                          <div className="flex items-start gap-4">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleSelectEmail(latestEmail.id);
                              }}
                              className="mt-1"
                            >
                              {isSelected ? (
                                <CheckSquare className="w-4 h-4 text-neon-cyan" />
                              ) : (
                                <Square className="w-4 h-4 text-gray-600" />
                              )}
                            </button>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleThread(threadId);
                                }}
                                className="text-neon-cyan hover:text-neon-pink transition-colors"
                              >
                                {isExpanded ? (
                                  <ChevronDown className="w-4 h-4" />
                                ) : (
                                  <ChevronRight className="w-4 h-4" />
                                )}
                              </button>
                              <span className="font-medium text-neon-cyan">
                                {latestEmail.from_address}
                              </span>
                              {threadEmails.length > 1 && (
                                <Badge variant="info" className="flex items-center gap-1">
                                  <MessageSquare className="w-3 h-3" />
                                  {threadEmails.length} messages
                                </Badge>
                              )}
                              {latestEmail.is_starred && (
                                <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                              )}
                              {threadEmails.length > 1 && !threadSummary && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleSummarizeThread(threadId, threadEmails);
                                  }}
                                  disabled={isSummarizing}
                                  className="h-6 px-2 text-xs"
                                >
                                  {isSummarizing ? (
                                    <>
                                      <Sparkles className="w-3 h-3 mr-1 animate-pulse" />
                                      Summarizing...
                                    </>
                                  ) : (
                                    <>
                                      <Sparkles className="w-3 h-3 mr-1" />
                                      Summarize
                                    </>
                                  )}
                                </Button>
                              )}
                            </div>
                            <p className="font-semibold mb-1 text-white">
                              {latestEmail.subject || '(No subject)'}
                            </p>
                            {threadSummary ? (
                              <div className="mt-2 p-3 bg-neon-cyan/10 rounded-lg border border-neon-cyan/20">
                                <p className="text-sm text-gray-300 mb-2">{threadSummary.summary}</p>
                                {threadSummary.key_points && threadSummary.key_points.length > 0 && (
                                  <ul className="text-xs text-gray-400 space-y-1">
                                    {threadSummary.key_points.map((point, idx) => (
                                      <li key={idx} className="flex items-start gap-2">
                                        <span className="text-neon-cyan">•</span>
                                        <span>{point}</span>
                                      </li>
                                    ))}
                                  </ul>
                                )}
                              </div>
                            ) : latestEmail.summary ? (
                              <p className="text-sm text-gray-400 line-clamp-2">{latestEmail.summary}</p>
                            ) : null}
                          </div>
                          <div className="flex gap-2">
                            {latestEmail.urgency_score && (
                              <Badge
                                variant={
                                  latestEmail.urgency_score > 70 ? 'error' :
                                  latestEmail.urgency_score > 40 ? 'warning' :
                                  'success'
                                }
                              >
                                {latestEmail.urgency_score}%
                              </Badge>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                if (latestEmail.is_starred) {
                                  unstarMutation.mutate(latestEmail.id);
                                } else {
                                  starMutation.mutate(latestEmail.id);
                                }
                              }}
                            >
                              <Star className={`w-4 h-4 ${latestEmail.is_starred ? 'fill-yellow-400 text-yellow-400' : ''}`} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                setPreviewEmail(latestEmail);
                              }}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                          </div>
                        </HolographicCard>
                      </motion.div>
                      {isExpanded && (
                          <div className="mt-4 pl-8 space-y-2 border-l-2 border-neon-cyan/20">
                            {threadEmails.slice(1).map((email, idx) => (
                              <motion.div
                                key={email.id}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                className="p-3 bg-dark-purple/50 rounded-lg hover:bg-dark-purple/70 transition-colors cursor-pointer"
                                onClick={() => setPreviewEmail(email)}
                              >
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="text-sm font-medium text-neon-cyan">{email.from_address}</span>
                                  <span className="text-xs text-gray-500">
                                    {new Date(email.occurred_at).toLocaleDateString('en-US', {
                                      month: 'short',
                                      day: 'numeric',
                                      hour: 'numeric',
                                      minute: 'numeric',
                                    })}
                                  </span>
                                  {email.is_starred && (
                                    <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                                  )}
                                </div>
                                <p className="text-sm text-gray-300 font-medium mb-1">{email.subject || '(No subject)'}</p>
                                {email.summary && (
                                  <p className="text-xs text-gray-400 line-clamp-2">{email.summary}</p>
                                )}
                              </motion.div>
                            ))}
                          </div>
                        )}
                      </Card>
                    );
                  })}

                  {/* Standalone Emails */}
                  {threadedEmails.standalone.map((email) => {
                    const isSelected = selectedEmails.has(email.id);

                    return (
                      <motion.div
                        key={email.id}
                        variants={fadeInUp}
                        whileHover={{ scale: 1.01 }}
                      >
                        <Card
                          className={`p-4 cursor-pointer transition-colors ${
                            isSelected ? 'border-neon-cyan bg-neon-cyan/10' : 'hover:border-neon-cyan'
                          } ${!email.is_archived ? 'border-l-4 border-l-neon-cyan' : ''}`}
                          onClick={() => setPreviewEmail(email)}
                        >
                          <div className="flex items-start gap-4">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleSelectEmail(email.id);
                              }}
                              className="mt-1"
                            >
                              {isSelected ? (
                                <CheckSquare className="w-4 h-4 text-neon-cyan" />
                              ) : (
                                <Square className="w-4 h-4 text-gray-600" />
                              )}
                            </button>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="font-medium text-neon-cyan">
                                  {email.from_address}
                                </span>
                                {email.is_starred && (
                                  <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                                )}
                              </div>
                              <p className="font-semibold mb-1 text-white">
                                {email.subject || '(No subject)'}
                              </p>
                              {email.summary && (
                                <p className="text-sm text-gray-400 line-clamp-2">{email.summary}</p>
                              )}
                            </div>
                            <div className="flex gap-2">
                              {email.urgency_score && (
                                <Badge
                                  variant={
                                    email.urgency_score > 70 ? 'error' :
                                    email.urgency_score > 40 ? 'warning' :
                                    'success'
                                  }
                                >
                                  {email.urgency_score}%
                                </Badge>
                              )}
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (email.is_starred) {
                                    unstarMutation.mutate(email.id);
                                  } else {
                                    starMutation.mutate(email.id);
                                  }
                                }}
                              >
                                <Star className={`w-4 h-4 ${email.is_starred ? 'fill-yellow-400 text-yellow-400' : ''}`} />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  archiveMutation.mutate(email.id);
                                }}
                              >
                                <Archive className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </Card>
                      </motion.div>
                    );
                  })}

                  {threadedEmails.threads.length === 0 && threadedEmails.standalone.length === 0 && (
                    <Card className="p-12 text-center">
                      <Mail className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                      <p className="text-gray-400">No emails found</p>
                    </Card>
                  )}
                </>
              )}
            </div>

            {/* Email Preview */}
            <div className="lg:col-span-1">
              <AnimatePresence>
                {previewEmail && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                  >
                    <Card className="p-6 sticky top-4">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-orbitron text-neon-cyan">Preview</h3>
                        <Button variant="ghost" size="sm" onClick={() => setPreviewEmail(null)}>
                          ×
                        </Button>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <p className="text-sm text-gray-400 mb-1">From</p>
                          <p className="text-white">{previewEmail.from_address}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-400 mb-1">Subject</p>
                          <p className="text-white font-semibold">{previewEmail.subject || '(No subject)'}</p>
                        </div>
                        
                        {/* AI Analysis Section */}
                        {emailAnalysis[previewEmail.id] && (
                          <div className="p-4 bg-neon-cyan/10 rounded-lg border border-neon-cyan/20">
                            <div className="flex items-center gap-2 mb-3">
                              <Brain className="w-5 h-5 text-neon-cyan" />
                              <h4 className="font-semibold text-neon-cyan">AI Analysis</h4>
                            </div>
                            {emailAnalysis[previewEmail.id].urgency && (
                              <div className="mb-2">
                                <span className="text-sm text-gray-400">Urgency: </span>
                                <Badge variant={emailAnalysis[previewEmail.id].urgency > 70 ? 'error' : emailAnalysis[previewEmail.id].urgency > 40 ? 'warning' : 'success'}>
                                  {emailAnalysis[previewEmail.id].urgency}%
                                </Badge>
                              </div>
                            )}
                            {emailAnalysis[previewEmail.id].sentiment && (
                              <div className="mb-2">
                                <span className="text-sm text-gray-400">Sentiment: </span>
                                <Badge variant={emailAnalysis[previewEmail.id].sentiment > 0 ? 'success' : emailAnalysis[previewEmail.id].sentiment < 0 ? 'error' : 'default'}>
                                  {emailAnalysis[previewEmail.id].sentiment > 0 ? 'Positive' : emailAnalysis[previewEmail.id].sentiment < 0 ? 'Negative' : 'Neutral'}
                                </Badge>
                              </div>
                            )}
                            {emailAnalysis[previewEmail.id].suggested_actions && emailAnalysis[previewEmail.id].suggested_actions.length > 0 && (
                              <div className="mt-3">
                                <p className="text-sm font-medium text-neon-cyan mb-2">Suggested Actions:</p>
                                <ul className="text-xs text-gray-300 space-y-1">
                                  {emailAnalysis[previewEmail.id].suggested_actions.map((action: string, idx: number) => (
                                    <li key={idx} className="flex items-start gap-2">
                                      <span className="text-neon-cyan">•</span>
                                      <span>{action}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {emailAnalysis[previewEmail.id].key_insights && (
                              <div className="mt-3">
                                <p className="text-sm font-medium text-neon-cyan mb-2">Key Insights:</p>
                                <p className="text-xs text-gray-300">{emailAnalysis[previewEmail.id].key_insights}</p>
                              </div>
                            )}
                          </div>
                        )}
                        
                        <div>
                          <p className="text-sm text-gray-400 mb-1">Body</p>
                          <div className="text-gray-300 whitespace-pre-wrap">
                            {previewEmail.body || previewEmail.summary || 'No content'}
                          </div>
                        </div>
                        <div className="flex gap-2 pt-4 border-t border-neon-cyan/20 flex-wrap">
                          {!emailAnalysis[previewEmail.id] && (
                            <Button 
                              variant="secondary" 
                              size="sm"
                              onClick={() => handleAnalyzeEmail(previewEmail.id)}
                              disabled={analyzingEmails.has(previewEmail.id)}
                            >
                              {analyzingEmails.has(previewEmail.id) ? (
                                <>
                                  <Brain className="w-4 h-4 mr-2 animate-pulse" />
                                  Analyzing...
                                </>
                              ) : (
                                <>
                                  <Brain className="w-4 h-4 mr-2" />
                                  Analyze Email
                                </>
                              )}
                            </Button>
                          )}
                          <Button 
                            variant="primary" 
                            size="sm"
                            onClick={() => handleGenerateDraft(previewEmail.id)}
                            disabled={generatingDraft}
                          >
                            {generatingDraft ? (
                              <>
                                <Sparkles className="w-4 h-4 mr-2 animate-pulse" />
                                Generating...
                              </>
                            ) : (
                              <>
                                <Sparkles className="w-4 h-4 mr-2" />
                                Generate Draft
                              </>
                            )}
                          </Button>
                          <Button 
                            variant="secondary" 
                            size="sm"
                            onClick={handleCreateTaskFromEmail}
                          >
                            <CheckCircle2 className="w-4 h-4 mr-2" />
                            Create Task
                          </Button>
                          <Button variant="secondary" size="sm">
                            <Reply className="w-4 h-4 mr-2" />
                            Reply
                          </Button>
                          <Button variant="secondary" size="sm">
                            <Forward className="w-4 h-4 mr-2" />
                            Forward
                          </Button>
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => {
                              if (previewEmail.is_starred) {
                                unstarMutation.mutate(previewEmail.id);
                              } else {
                                starMutation.mutate(previewEmail.id);
                              }
                            }}
                          >
                            {previewEmail.is_starred ? 'Unstar' : 'Star'}
                          </Button>
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => {
                              if (previewEmail.is_archived) {
                                unarchiveMutation.mutate(previewEmail.id);
                              } else {
                                archiveMutation.mutate(previewEmail.id);
                              }
                            }}
                          >
                            {previewEmail.is_archived ? 'Unarchive' : 'Archive'}
                          </Button>
                          <Button
                            variant="error"
                            size="sm"
                            onClick={() => deleteMutation.mutate(previewEmail.id)}
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete
                          </Button>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Draft Generation Dialog */}
          {showDraftDialog && generatedDrafts.length > 0 && (
            <Dialog
              isOpen={showDraftDialog}
              onClose={() => {
                setShowDraftDialog(false);
                setGeneratedDrafts([]);
              }}
              title="Generated Drafts"
              size="lg"
            >
              <div className="space-y-4">
                <p className="text-sm text-gray-400">
                  {generatedDrafts.length} draft variant{generatedDrafts.length > 1 ? 's' : ''} generated. Select one to edit or send.
                </p>
                {generatedDrafts.map((draft: any, idx: number) => (
                  <Card key={draft.id || idx} className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-white">Variant {idx + 1}</h4>
                      <Badge variant="info">
                        {draft.confidence_score ? `${Math.round(draft.confidence_score * 100)}% confidence` : 'Draft'}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-300 whitespace-pre-wrap mb-3">
                      {draft.content || draft.body || 'No content'}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          router.push(`/drafts?edit=${draft.id}`);
                          setShowDraftDialog(false);
                        }}
                      >
                        Edit Draft
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={async () => {
                          try {
                            await draftAPI.sendDraft(draft.id);
                            toast.success('Draft sent');
                            setShowDraftDialog(false);
                            setGeneratedDrafts([]);
                            refetch();
                          } catch (error) {
                            toast.error('Failed to send draft');
                          }
                        }}
                      >
                        Send
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </Dialog>
          )}

          {/* Create Task Dialog */}
          {showCreateTaskDialog && previewEmail && (
            <Dialog
              isOpen={showCreateTaskDialog}
              onClose={() => {
                setShowCreateTaskDialog(false);
                setTaskFormData({
                  title: '',
                  description: '',
                  task_type: 'follow_up',
                  priority: 'medium',
                  due_date: '',
                  due_time: '',
                });
              }}
              title="Create Task from Email"
              size="md"
            >
              <div className="space-y-4">
                <div className="p-3 bg-neon-cyan/10 rounded-lg border border-neon-cyan/20 mb-4">
                  <p className="text-xs text-gray-400 mb-1">From Email:</p>
                  <p className="text-sm text-white font-medium">{previewEmail.subject || '(No subject)'}</p>
                  <p className="text-xs text-gray-400 mt-1">{previewEmail.from_address}</p>
                </div>
                
                <Input
                  label="Task Title *"
                  value={taskFormData.title}
                  onChange={(e) => setTaskFormData({ ...taskFormData, title: e.target.value })}
                  placeholder="Enter task title"
                  required
                />
                
                <div>
                  <label className="block text-sm font-medium text-neon-cyan mb-2">Task Type</label>
                  <Select
                    options={[
                      { value: 'follow_up', label: 'Follow Up' },
                      { value: 'showing', label: 'Showing' },
                      { value: 'inspection', label: 'Inspection' },
                      { value: 'appraisal', label: 'Appraisal' },
                      { value: 'signing', label: 'Signing' },
                      { value: 'deadline', label: 'Deadline' },
                      { value: 'call', label: 'Call' },
                      { value: 'general', label: 'General' },
                    ]}
                    value={taskFormData.task_type}
                    onChange={(value) => setTaskFormData({ ...taskFormData, task_type: value })}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-neon-cyan mb-2">Priority</label>
                  <Select
                    options={[
                      { value: 'low', label: 'Low' },
                      { value: 'medium', label: 'Medium' },
                      { value: 'high', label: 'High' },
                    ]}
                    value={taskFormData.priority}
                    onChange={(value) => setTaskFormData({ ...taskFormData, priority: value })}
                  />
                </div>
                
                <Textarea
                  label="Description"
                  value={taskFormData.description}
                  onChange={(e) => setTaskFormData({ ...taskFormData, description: e.target.value })}
                  placeholder="Task description (pre-filled from email)"
                  rows={4}
                />
                
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Due Date"
                    type="date"
                    value={taskFormData.due_date}
                    onChange={(e) => setTaskFormData({ ...taskFormData, due_date: e.target.value })}
                  />
                  <Input
                    label="Due Time"
                    type="time"
                    value={taskFormData.due_time}
                    onChange={(e) => setTaskFormData({ ...taskFormData, due_time: e.target.value })}
                  />
                </div>
                
                <div className="flex gap-4 justify-end pt-4 border-t border-neon-cyan/20">
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setShowCreateTaskDialog(false);
                      setTaskFormData({
                        title: '',
                        description: '',
                        task_type: 'follow_up',
                        priority: 'medium',
                        due_date: '',
                        due_time: '',
                      });
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleSubmitTask}
                    disabled={!taskFormData.title.trim()}
                  >
                    <CheckCircle2 className="w-4 h-4 mr-2" />
                    Create Task
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
