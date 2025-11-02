'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { integrationsAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { 
  Mail, 
  Twitter, 
  Facebook, 
  Plus, 
  Trash2, 
  Power, 
  PowerOff,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { toast } from 'react-hot-toast';
import { ConfirmationDialog } from '@/components/ui/drawer';

interface EmailAccount {
  id: number;
  provider: string;
  email_address: string;
  is_active: boolean;
  is_primary: boolean;
  sync_status: string;
  last_sync_at: string | null;
  created_at: string;
}

interface SocialAccount {
  id: number;
  provider: string;
  handle: string;
  display_name: string | null;
  is_active: boolean;
  created_at: string;
}

export default function IntegrationsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [disconnectDialog, setDisconnectDialog] = useState<{ type: 'email' | 'social'; id: number; name: string } | null>(null);

  const { data: emailAccounts, isLoading: isLoadingEmail, refetch: refetchEmail } = useAPI(
    ['integrations', 'email-accounts'],
    () => integrationsAPI.listEmailAccounts(),
    { enabled: isAuthenticated }
  );

  const { data: socialAccounts, isLoading: isLoadingSocial, refetch: refetchSocial } = useAPI(
    ['integrations', 'social-accounts'],
    () => integrationsAPI.listSocialAccounts(),
    { enabled: isAuthenticated }
  );

  const disconnectEmailMutation = useAPIMutation(
    (id: number) => integrationsAPI.disconnectEmailAccount(id),
    {
      onSuccess: () => {
        toast.success('Email account disconnected');
        refetchEmail();
        setDisconnectDialog(null);
      },
      onError: () => {
        toast.error('Failed to disconnect email account');
      },
    }
  );

  const disconnectSocialMutation = useAPIMutation(
    (id: number) => integrationsAPI.disconnectSocialAccount(id),
    {
      onSuccess: () => {
        toast.success('Social account disconnected');
        refetchSocial();
        setDisconnectDialog(null);
      },
      onError: () => {
        toast.error('Failed to disconnect social account');
      },
    }
  );

  const toggleEmailMutation = useAPIMutation(
    ({ id, enable }: { id: number; enable: boolean }) => integrationsAPI.toggleEmailAccount(id, enable),
    {
      onSuccess: () => {
        toast.success('Email account sync toggled');
        refetchEmail();
      },
    }
  );

  const syncEmailMutation = useAPIMutation(
    (id: number) => integrationsAPI.triggerEmailSync(id),
    {
      onSuccess: () => {
        toast.success('Email sync initiated');
      },
      onError: () => {
        toast.error('Failed to trigger sync');
      },
    }
  );

  const handleConnect = async (provider: 'gmail' | 'outlook' | 'twitter' | 'facebook') => {
    try {
      let authUrl: string;
      switch (provider) {
        case 'gmail':
          const gmailResp = await integrationsAPI.getGmailAuthUrl();
          authUrl = gmailResp.auth_url;
          break;
        case 'outlook':
          const outlookResp = await integrationsAPI.getOutlookAuthUrl();
          authUrl = outlookResp.auth_url;
          break;
        case 'twitter':
          const twitterResp = await integrationsAPI.getTwitterAuthUrl();
          authUrl = twitterResp.auth_url;
          break;
        case 'facebook':
          const facebookResp = await integrationsAPI.getFacebookAuthUrl();
          authUrl = facebookResp.auth_url;
          break;
        default:
          throw new Error('Invalid provider');
      }
      window.location.href = authUrl;
    } catch (error) {
      toast.error('Failed to initiate connection');
    }
  };

  const handleDisconnect = (type: 'email' | 'social', id: number, name: string) => {
    setDisconnectDialog({ type, id, name });
  };

  const confirmDisconnect = () => {
    if (!disconnectDialog) return;
    if (disconnectDialog.type === 'email') {
      disconnectEmailMutation.mutate(disconnectDialog.id);
    } else {
      disconnectSocialMutation.mutate(disconnectDialog.id);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
    });
  };

  const getSyncStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'syncing':
        return <Badge variant="info">Syncing</Badge>;
      case 'success':
        return <Badge variant="success">Synced</Badge>;
      case 'error':
        return <Badge variant="error">Error</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
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
          <div>
            <h1 className="text-4xl font-orbitron font-bold text-transparent bg-clip-text bg-gradient-neon mb-2">
              Integrations
            </h1>
            <p className="text-gray-400">Manage your connected accounts and services</p>
          </div>

          {/* Email Accounts */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-orbitron font-bold text-neon-cyan flex items-center gap-2">
                <Mail className="w-6 h-6" />
                Email Accounts
              </h2>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleConnect('gmail')}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Connect Gmail
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleConnect('outlook')}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Connect Outlook
                </Button>
              </div>
            </div>

            {isLoadingEmail ? (
              <div className="text-center py-8 text-gray-400">Loading email accounts...</div>
            ) : emailAccounts && emailAccounts.length > 0 ? (
              <div className="space-y-4">
                {(emailAccounts as EmailAccount[]).map((account) => (
                  <motion.div
                    key={account.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-dark-purple/50 border border-neon-cyan/20 rounded-lg"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <Mail className="w-5 h-5 text-neon-cyan" />
                          <span className="font-semibold text-white">{account.email_address}</span>
                          {account.is_primary && (
                            <Badge variant="neon">Primary</Badge>
                          )}
                          {getSyncStatusBadge(account.sync_status)}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span>Provider: {account.provider}</span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            Last sync: {formatDate(account.last_sync_at)}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => syncEmailMutation.mutate(account.id)}
                          disabled={syncEmailMutation.isPending}
                        >
                          <RefreshCw className={`w-4 h-4 ${syncEmailMutation.isPending ? 'animate-spin' : ''}`} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleEmailMutation.mutate({ id: account.id, enable: !account.is_active })}
                        >
                          {account.is_active ? (
                            <PowerOff className="w-4 h-4 text-yellow-400" />
                          ) : (
                            <Power className="w-4 h-4 text-green-400" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDisconnect('email', account.id, account.email_address)}
                        >
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Mail className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <p>No email accounts connected</p>
                <p className="text-sm mt-2">Connect your Gmail or Outlook account to get started</p>
              </div>
            )}
          </Card>

          {/* Social Accounts */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-orbitron font-bold text-neon-pink flex items-center gap-2">
                <Twitter className="w-6 h-6" />
                Social Accounts
              </h2>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleConnect('twitter')}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Connect Twitter
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleConnect('facebook')}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Connect Facebook
                </Button>
              </div>
            </div>

            {isLoadingSocial ? (
              <div className="text-center py-8 text-gray-400">Loading social accounts...</div>
            ) : socialAccounts && socialAccounts.length > 0 ? (
              <div className="space-y-4">
                {(socialAccounts as SocialAccount[]).map((account) => (
                  <motion.div
                    key={account.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-dark-purple/50 border border-neon-pink/20 rounded-lg"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          {account.provider === 'twitter' ? (
                            <Twitter className="w-5 h-5 text-blue-400" />
                          ) : (
                            <Facebook className="w-5 h-5 text-blue-500" />
                          )}
                          <span className="font-semibold text-white">
                            @{account.handle}
                          </span>
                          {account.display_name && (
                            <span className="text-gray-400">({account.display_name})</span>
                          )}
                          {account.is_active ? (
                            <Badge variant="success">Active</Badge>
                          ) : (
                            <Badge variant="error">Inactive</Badge>
                          )}
                        </div>
                        <div className="text-sm text-gray-400">
                          Provider: {account.provider}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDisconnect('social', account.id, account.handle)}
                        >
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Twitter className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <p>No social accounts connected</p>
                <p className="text-sm mt-2">Connect your Twitter or Facebook account to manage messages</p>
              </div>
            )}
          </Card>

          {/* Disconnect Confirmation Dialog */}
          {disconnectDialog && (
            <ConfirmationDialog
              isOpen={!!disconnectDialog}
              onClose={() => setDisconnectDialog(null)}
              onConfirm={confirmDisconnect}
              title={`Disconnect ${disconnectDialog.type === 'email' ? 'Email' : 'Social'} Account`}
              message={`Are you sure you want to disconnect ${disconnectDialog.name}? This action cannot be undone.`}
              confirmText="Disconnect"
              cancelText="Cancel"
              variant="danger"
            />
          )}
        </motion.div>
      </div>
    </div>
  );
}

