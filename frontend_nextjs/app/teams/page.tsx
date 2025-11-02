'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input, Textarea } from '@/components/ui/input';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { teamAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { 
  Users, 
  Plus, 
  Trash2, 
  Edit, 
  Mail, 
  UserPlus,
  CheckCircle,
  XCircle,
  Clock,
  Activity
} from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { toast } from 'react-hot-toast';
import { Dialog } from '@/components/ui/drawer';
import { ConfirmationDialog } from '@/components/ui/drawer';
import { useAuthStore } from '@/lib/stores/authStore';

interface Team {
  id: number;
  name: string;
  description?: string | null;
  owner_id: number;
  settings: Record<string, any>;
  logo_url?: string | null;
  website?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at?: string | null;
  members?: TeamMember[];
}

interface TeamMember {
  id: number;
  team_id: number;
  user_id: number;
  role: string;
  status: string;
  invited_at: string;
  joined_at?: string | null;
}

interface Activity {
  timestamp: string;
  user_id: number;
  user_name: string;
  activity_type: string;
  description: string;
  entity_type?: string | null;
  entity_id?: number | null;
}

export default function TeamsPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuth();
  const { accessToken } = useAuthStore();
  const [isCreatingTeam, setIsCreatingTeam] = useState(false);
  const [isEditingTeam, setIsEditingTeam] = useState(false);
  const [isInvitingMember, setIsInvitingMember] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [teamName, setTeamName] = useState('');
  const [teamDescription, setTeamDescription] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'member' | 'admin'>('member');
  const [deleteDialog, setDeleteDialog] = useState<{ teamId: number; teamName: string } | null>(null);
  const [removeMemberDialog, setRemoveMemberDialog] = useState<{ memberId: number; memberName: string } | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'members' | 'activity'>('overview');

  // Try to get user's team (they can only own one)
  // For now, we'll assume they need to create one or we'll need a backend endpoint to find their team
  // Since backend doesn't have a list endpoint, we'll handle team creation/access differently
  const [teamId, setTeamId] = useState<number | null>(null);

  const { data: team, isLoading: isLoadingTeam, refetch: refetchTeam } = useAPI(
    ['team', teamId],
    () => teamId ? teamAPI.getTeam(teamId) : Promise.resolve(null),
    { enabled: isAuthenticated && !!teamId }
  );

  const { data: members, isLoading: isLoadingMembers, refetch: refetchMembers } = useAPI(
    ['team-members', teamId],
    () => teamId ? teamAPI.listTeamMembers(teamId) : Promise.resolve([]),
    { enabled: isAuthenticated && !!teamId }
  );

  const { data: activities, isLoading: isLoadingActivities, refetch: refetchActivity } = useAPI(
    ['team-activity', teamId],
    () => teamId ? teamAPI.getTeamActivity(teamId) : Promise.resolve([]),
    { enabled: isAuthenticated && !!teamId }
  );

  const createTeamMutation = useAPIMutation(
    (data: { name: string; description?: string }) => teamAPI.createTeam(data),
    {
      onSuccess: (data) => {
        toast.success('Team created successfully');
        setTeamId(data.id);
        setIsCreatingTeam(false);
        setTeamName('');
        setTeamDescription('');
        refetchTeam();
      },
      onError: (error: any) => {
        const message = error?.response?.data?.detail || 'Failed to create team';
        toast.error(message);
      },
    }
  );

  const updateTeamMutation = useAPIMutation(
    ({ id, data }: { id: number; data: any }) => teamAPI.updateTeam(id, data),
    {
      onSuccess: () => {
        toast.success('Team updated successfully');
        setIsEditingTeam(false);
        refetchTeam();
      },
    }
  );

  const deleteTeamMutation = useAPIMutation(
    (id: number) => teamAPI.deleteTeam(id),
    {
      onSuccess: () => {
        toast.success('Team deleted');
        setTeamId(null);
        setSelectedTeam(null);
        setDeleteDialog(null);
      },
    }
  );

  const inviteMemberMutation = useAPIMutation(
    ({ teamId, email, role }: { teamId: number; email: string; role: 'member' | 'admin' }) => 
      teamAPI.inviteMember(teamId, email, role),
    {
      onSuccess: () => {
        toast.success('Member invited successfully');
        setIsInvitingMember(false);
        setInviteEmail('');
        setInviteRole('member');
        refetchMembers();
      },
      onError: (error: any) => {
        const message = error?.response?.data?.detail || 'Failed to invite member';
        toast.error(message);
      },
    }
  );

  const removeMemberMutation = useAPIMutation(
    ({ teamId, memberId }: { teamId: number; memberId: number }) => 
      teamAPI.removeMember(teamId, memberId),
    {
      onSuccess: () => {
        toast.success('Member removed');
        setRemoveMemberDialog(null);
        refetchMembers();
      },
    }
  );

  const handleCreateTeam = () => {
    if (!teamName.trim()) {
      toast.error('Team name is required');
      return;
    }
    createTeamMutation.mutate({
      name: teamName,
      description: teamDescription || undefined,
    });
  };

  const handleUpdateTeam = () => {
    if (!selectedTeam || !teamName.trim()) {
      toast.error('Team name is required');
      return;
    }
    updateTeamMutation.mutate({
      id: selectedTeam.id,
      data: {
        name: teamName,
        description: teamDescription || undefined,
      },
    });
  };

  const handleInviteMember = () => {
    if (!teamId || !inviteEmail.trim()) {
      toast.error('Email is required');
      return;
    }
    inviteMemberMutation.mutate({
      teamId,
      email: inviteEmail,
      role: inviteRole,
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
    });
  };

  const getRoleBadge = (role: string) => {
    return role === 'admin' ? (
      <Badge variant="neon">Admin</Badge>
    ) : (
      <Badge variant="info">Member</Badge>
    );
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <Badge variant="success">Active</Badge>;
      case 'invited':
        return <Badge variant="warning">Invited</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    if (team) {
      setSelectedTeam(team);
      setTeamName(team.name);
      setTeamDescription(team.description || '');
    }
  }, [team]);

  if (!isAuthenticated) {
    return null;
  }

  const isOwner = team && user && team.owner_id === user.id;

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
                Teams
              </h1>
              <p className="text-gray-400">Manage your team and collaboration</p>
            </div>
            {!team && (
              <Button
                variant="primary"
                onClick={() => setIsCreatingTeam(true)}
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Team
              </Button>
            )}
          </div>

          {!teamId && !team && (
            <Card className="p-12 text-center">
              <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Team Yet</h3>
              <p className="text-gray-400 mb-6">
                Create a team to collaborate with your colleagues and share contacts
              </p>
              <Button variant="primary" onClick={() => setIsCreatingTeam(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Team
              </Button>
            </Card>
          )}

          {team && (
            <>
              {/* Team Header */}
              <Card className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-2xl font-orbitron font-bold text-neon-cyan">
                        {team.name}
                      </h2>
                      {isOwner && <Badge variant="neon">Owner</Badge>}
                      {team.is_active ? (
                        <Badge variant="success">Active</Badge>
                      ) : (
                        <Badge variant="error">Inactive</Badge>
                      )}
                    </div>
                    {team.description && (
                      <p className="text-gray-400 mb-4">{team.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>Created: {formatDate(team.created_at)}</span>
                      {team.updated_at && (
                        <span>Updated: {formatDate(team.updated_at)}</span>
                      )}
                    </div>
                  </div>
                  {isOwner && (
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setIsEditingTeam(true);
                          setTeamName(team.name);
                          setTeamDescription(team.description || '');
                        }}
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Edit
                      </Button>
                      <Button
                        variant="error"
                        size="sm"
                        onClick={() => setDeleteDialog({ teamId: team.id, teamName: team.name })}
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete
                      </Button>
                    </div>
                  )}
                </div>
              </Card>

              {/* Tabs */}
              <div className="flex gap-2 border-b border-neon-cyan/20">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`px-4 py-2 font-medium transition-colors ${
                    activeTab === 'overview'
                      ? 'text-neon-cyan border-b-2 border-neon-cyan'
                      : 'text-gray-400 hover:text-neon-cyan'
                  }`}
                >
                  Overview
                </button>
                <button
                  onClick={() => setActiveTab('members')}
                  className={`px-4 py-2 font-medium transition-colors ${
                    activeTab === 'members'
                      ? 'text-neon-cyan border-b-2 border-neon-cyan'
                      : 'text-gray-400 hover:text-neon-cyan'
                  }`}
                >
                  Members ({members?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('activity')}
                  className={`px-4 py-2 font-medium transition-colors ${
                    activeTab === 'activity'
                      ? 'text-neon-cyan border-b-2 border-neon-cyan'
                      : 'text-gray-400 hover:text-neon-cyan'
                  }`}
                >
                  Activity
                </button>
              </div>

              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <Card className="p-6">
                  <h3 className="text-xl font-orbitron text-neon-cyan mb-4">Team Overview</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-dark-purple/50 rounded-lg p-4">
                      <div className="text-sm text-gray-400 mb-1">Total Members</div>
                      <div className="text-2xl font-bold text-neon-cyan">{members?.length || 0}</div>
                    </div>
                    <div className="bg-dark-purple/50 rounded-lg p-4">
                      <div className="text-sm text-gray-400 mb-1">Active Members</div>
                      <div className="text-2xl font-bold text-green-400">
                        {members?.filter((m: TeamMember) => m.status === 'active').length || 0}
                      </div>
                    </div>
                    <div className="bg-dark-purple/50 rounded-lg p-4">
                      <div className="text-sm text-gray-400 mb-1">Recent Activity</div>
                      <div className="text-2xl font-bold text-neon-pink">{activities?.length || 0}</div>
                    </div>
                  </div>
                </Card>
              )}

              {/* Members Tab */}
              {activeTab === 'members' && (
                <Card className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-orbitron text-neon-cyan">Team Members</h3>
                    {isOwner && (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setIsInvitingMember(true)}
                      >
                        <UserPlus className="w-4 h-4 mr-2" />
                        Invite Member
                      </Button>
                    )}
                  </div>

                  {isLoadingMembers ? (
                    <div className="text-center py-8 text-gray-400">Loading members...</div>
                  ) : members && members.length > 0 ? (
                    <div className="space-y-4">
                      {(members as TeamMember[]).map((member) => (
                        <motion.div
                          key={member.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="p-4 bg-dark-purple/50 border border-neon-cyan/20 rounded-lg"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                              <div className="w-10 h-10 rounded-full bg-neon-cyan/20 flex items-center justify-center">
                                <Users className="w-5 h-5 text-neon-cyan" />
                              </div>
                              <div>
                                <div className="flex items-center gap-2">
                                  <span className="font-semibold text-white">User #{member.user_id}</span>
                                  {getRoleBadge(member.role)}
                                  {getStatusBadge(member.status)}
                                </div>
                                <div className="text-sm text-gray-400">
                                  Invited: {formatDate(member.invited_at)}
                                  {member.joined_at && ` • Joined: ${formatDate(member.joined_at)}`}
                                </div>
                              </div>
                            </div>
                            {isOwner && member.role !== 'admin' && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setRemoveMemberDialog({ 
                                  memberId: member.id, 
                                  memberName: `User #${member.user_id}` 
                                })}
                              >
                                <Trash2 className="w-4 h-4 text-red-400" />
                              </Button>
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-gray-400">
                      <Users className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                      <p>No members yet</p>
                      {isOwner && (
                        <p className="text-sm mt-2">Invite team members to get started</p>
                      )}
                    </div>
                  )}
                </Card>
              )}

              {/* Activity Tab */}
              {activeTab === 'activity' && (
                <Card className="p-6">
                  <h3 className="text-xl font-orbitron text-neon-cyan mb-4">Team Activity</h3>
                  {isLoadingActivities ? (
                    <div className="text-center py-8 text-gray-400">Loading activity...</div>
                  ) : activities && activities.length > 0 ? (
                    <div className="space-y-4">
                      {(activities as Activity[]).map((activity, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="p-4 bg-dark-purple/50 border-l-4 border-neon-cyan/50 rounded-lg"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <Activity className="w-4 h-4 text-neon-cyan" />
                                <span className="font-semibold text-white">{activity.user_name}</span>
                                <span className="text-gray-400">•</span>
                                <span className="text-sm text-gray-400">{formatDate(activity.timestamp)}</span>
                              </div>
                              <p className="text-gray-300">{activity.description}</p>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-gray-400">
                      <Activity className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                      <p>No activity yet</p>
                    </div>
                  )}
                </Card>
              )}
            </>
          )}

          {/* Create Team Dialog */}
          {isCreatingTeam && (
            <Dialog
              isOpen={isCreatingTeam}
              onClose={() => {
                setIsCreatingTeam(false);
                setTeamName('');
                setTeamDescription('');
              }}
              title="Create Team"
              size="md"
            >
              <div className="space-y-4">
                <Input
                  label="Team Name"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  placeholder="Enter team name"
                  required
                />
                <Textarea
                  label="Description"
                  value={teamDescription}
                  onChange={(e) => setTeamDescription(e.target.value)}
                  placeholder="Enter team description (optional)"
                  rows={3}
                />
                <div className="flex gap-4 justify-end pt-4 border-t border-neon-cyan/20">
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setIsCreatingTeam(false);
                      setTeamName('');
                      setTeamDescription('');
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleCreateTeam}
                    disabled={!teamName.trim() || createTeamMutation.isPending}
                  >
                    Create Team
                  </Button>
                </div>
              </div>
            </Dialog>
          )}

          {/* Edit Team Dialog */}
          {isEditingTeam && selectedTeam && (
            <Dialog
              isOpen={isEditingTeam}
              onClose={() => {
                setIsEditingTeam(false);
                setTeamName(selectedTeam.name);
                setTeamDescription(selectedTeam.description || '');
              }}
              title="Edit Team"
              size="md"
            >
              <div className="space-y-4">
                <Input
                  label="Team Name"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  placeholder="Enter team name"
                  required
                />
                <Textarea
                  label="Description"
                  value={teamDescription}
                  onChange={(e) => setTeamDescription(e.target.value)}
                  placeholder="Enter team description (optional)"
                  rows={3}
                />
                <div className="flex gap-4 justify-end pt-4 border-t border-neon-cyan/20">
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setIsEditingTeam(false);
                      setTeamName(selectedTeam.name);
                      setTeamDescription(selectedTeam.description || '');
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleUpdateTeam}
                    disabled={!teamName.trim() || updateTeamMutation.isPending}
                  >
                    Save Changes
                  </Button>
                </div>
              </div>
            </Dialog>
          )}

          {/* Invite Member Dialog */}
          {isInvitingMember && teamId && (
            <Dialog
              isOpen={isInvitingMember}
              onClose={() => {
                setIsInvitingMember(false);
                setInviteEmail('');
                setInviteRole('member');
              }}
              title="Invite Team Member"
              size="md"
            >
              <div className="space-y-4">
                <Input
                  label="Email Address"
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="user@example.com"
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-neon-cyan mb-2">
                    Role
                  </label>
                  <div className="flex gap-2">
                    <Button
                      variant={inviteRole === 'member' ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => setInviteRole('member')}
                    >
                      Member
                    </Button>
                    <Button
                      variant={inviteRole === 'admin' ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => setInviteRole('admin')}
                    >
                      Admin
                    </Button>
                  </div>
                </div>
                <div className="flex gap-4 justify-end pt-4 border-t border-neon-cyan/20">
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setIsInvitingMember(false);
                      setInviteEmail('');
                      setInviteRole('member');
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleInviteMember}
                    disabled={!inviteEmail.trim() || inviteMemberMutation.isPending}
                  >
                    <UserPlus className="w-4 h-4 mr-2" />
                    Send Invitation
                  </Button>
                </div>
              </div>
            </Dialog>
          )}

          {/* Delete Team Confirmation */}
          {deleteDialog && (
            <ConfirmationDialog
              isOpen={!!deleteDialog}
              onClose={() => setDeleteDialog(null)}
              onConfirm={() => {
                deleteTeamMutation.mutate(deleteDialog.teamId);
              }}
              title="Delete Team"
              message={`Are you sure you want to delete "${deleteDialog.teamName}"? This action cannot be undone and will remove all team members.`}
              confirmText="Delete"
              cancelText="Cancel"
              variant="danger"
            />
          )}

          {/* Remove Member Confirmation */}
          {removeMemberDialog && teamId && (
            <ConfirmationDialog
              isOpen={!!removeMemberDialog}
              onClose={() => setRemoveMemberDialog(null)}
              onConfirm={() => {
                removeMemberMutation.mutate({
                  teamId,
                  memberId: removeMemberDialog.memberId,
                });
              }}
              title="Remove Team Member"
              message={`Are you sure you want to remove ${removeMemberDialog.memberName} from the team?`}
              confirmText="Remove"
              cancelText="Cancel"
              variant="danger"
            />
          )}
        </motion.div>
      </div>
    </div>
  );
}

