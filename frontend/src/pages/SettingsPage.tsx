import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '../stores/authStore'
import api, { integrationService } from '../services/api'
import toast from 'react-hot-toast'
import {
  EnvelopeIcon,
  Cog6ToothIcon,
  UserIcon,
  BellIcon,
  ShieldCheckIcon,
  BoltIcon,
  ChatBubbleLeftRightIcon,
  PlusIcon
} from '@heroicons/react/24/outline'

export default function SettingsPage() {
  const { user } = useAuthStore()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('email-accounts')

  const { data: emailAccounts, isLoading: loadingEmail } = useQuery({
    queryKey: ['email-accounts'],
    queryFn: integrationService.listEmailAccounts
  })

  const { data: socialAccounts, isLoading: loadingSocial } = useQuery({
    queryKey: ['social-accounts'],
    queryFn: integrationService.listSocialAccounts
  })

  const connectGmailMutation = useMutation({
    mutationFn: async () => {
      const response = await api.get('/integrations/gmail/authorize')
      return response.data
    },
    onSuccess: (data) => {
      window.location.href = data.auth_url
    },
    onError: () => {
      toast.error('Failed to initiate Gmail connection')
    },
  })

  const connectOutlookMutation = useMutation({
    mutationFn: async () => {
      const response = await api.get('/integrations/outlook/authorize')
      return response.data
    },
    onSuccess: (data) => {
      window.location.href = data.auth_url
    },
    onError: () => {
      toast.error('Failed to initiate Outlook connection')
    },
  })

  const connectTwitterMutation = useMutation({
    mutationFn: async () => {
      const response = await api.get('/integrations/twitter/authorize')
      return response.data
    },
    onSuccess: (data) => {
      window.location.href = data.auth_url
    }
  })

  const connectFacebookMutation = useMutation({
    mutationFn: async () => {
      const response = await api.get('/integrations/facebook/authorize')
      return response.data
    },
    onSuccess: (data) => {
      window.location.href = data.auth_url
    }
  })

  const disconnectSocialMutation = useMutation({
    mutationFn: integrationService.disconnectSocialAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['social-accounts'] })
      toast.success('Social account disconnected')
    }
  })

  const disconnectEmailMutation = useMutation({
    mutationFn: integrationService.disconnectEmailAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email-accounts'] })
      toast.success('Email account disconnected')
    }
  })

  const tabs = [
    { id: 'email-accounts', label: 'Email Accounts', icon: EnvelopeIcon },
    { id: 'social-accounts', label: 'Social Channels', icon: ChatBubbleLeftRightIcon },
    { id: 'automation', label: 'Automation Rules', icon: BoltIcon },
    { id: 'profile', label: 'Profile', icon: UserIcon },
    { id: 'preferences', label: 'Preferences', icon: Cog6ToothIcon },
    { id: 'notifications', label: 'Notifications', icon: BellIcon },
    { id: 'security', label: 'Security', icon: ShieldCheckIcon },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
        <p className="text-gray-600 mt-1">Manage your account, channels, and automation preferences</p>
      </div>

      <div className="border-b border-gray-200 overflow-x-auto">
        <nav className="-mb-px flex space-x-8 min-w-max">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              <tab.icon className="h-5 w-5 mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {activeTab === 'email-accounts' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Connected Email Accounts</h3>
              <p className="text-sm text-gray-600">
                Connect Gmail or Outlook to enable AI triage, drafting, and automation.
              </p>
            </div>
            {loadingEmail ? (
              <LoadingSkeleton />
            ) : emailAccounts && emailAccounts.length > 0 ? (
              <div className="space-y-3">
                {emailAccounts.map((account: any) => (
                  <AccountRow
                    key={account.id}
                    title={account.email_address}
                    subtitle={account.provider === 'gmail' ? 'Gmail' : 'Outlook'}
                    status={account.is_active ? 'Active' : 'Inactive'}
                    onDisconnect={() => disconnectEmailMutation.mutate(account.id)}
                  />
                ))}
              </div>
            ) : (
              <EmptyState message="No email accounts connected" />
            )}

            <div className="pt-4 border-t border-gray-200">
              <h4 className="font-medium text-gray-900 mb-3">Connect New Account</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <ConnectButton
                  label="Connect Gmail"
                  onClick={() => connectGmailMutation.mutate()}
                  loading={connectGmailMutation.isPending}
                />
                <ConnectButton
                  label="Connect Outlook"
                  onClick={() => connectOutlookMutation.mutate()}
                  loading={connectOutlookMutation.isPending}
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'social-accounts' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Social Channels</h3>
              <p className="text-sm text-gray-600">
                Bring Twitter/X DMs and Facebook Messenger conversations into your unified inbox.
              </p>
            </div>
            {loadingSocial ? (
              <LoadingSkeleton />
            ) : socialAccounts && socialAccounts.length > 0 ? (
              <div className="space-y-3">
                {socialAccounts.map((account: any) => (
                  <AccountRow
                    key={account.id}
                    title={account.handle}
                    subtitle={account.provider.replace('_', ' ')}
                    status={account.is_active ? 'Active' : 'Inactive'}
                    onDisconnect={() => disconnectSocialMutation.mutate(account.id)}
                  />
                ))}
              </div>
            ) : (
              <EmptyState message="No social accounts connected" />
            )}

            <div className="pt-4 border-t border-gray-200">
              <h4 className="font-medium text-gray-900 mb-3">Connect New Channel</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <ConnectButton
                  label="Connect Twitter/X"
                  onClick={() => connectTwitterMutation.mutate()}
                  loading={connectTwitterMutation.isPending}
                />
                <ConnectButton
                  label="Connect Facebook Messenger"
                  onClick={() => connectFacebookMutation.mutate()}
                  loading={connectFacebookMutation.isPending}
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'automation' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Automation Rules</h3>
                <p className="text-sm text-gray-600">Build custom triggers and actions for your workflow.</p>
              </div>
              <button className="btn-primary flex items-center">
                <PlusIcon className="h-5 w-5 mr-2" />
                Create Rule
              </button>
            </div>
            <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg p-6 text-center text-sm text-gray-600">
              Visual rule builder coming soon. Draft rules will appear here once created.
            </div>
          </div>
        )}

        {activeTab === 'profile' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Profile Information</h3>
            <ProfileField label="Full Name" value={user?.full_name || ''} />
            <ProfileField label="Email" value={user?.email || ''} />
            <ProfileField label="Subscription" value={user?.subscription_tier?.replace('_', ' ').toUpperCase() || 'FREE TRIAL'} />
          </div>
        )}

        {activeTab === 'preferences' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Preferences</h3>
            <p className="text-sm text-gray-600">Localisation, voice style, and custom settings coming soon.</p>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
            <p className="text-sm text-gray-600">Configure email, in-app, and SMS notifications.</p>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Security</h3>
            <p className="text-sm text-gray-600">Two-factor authentication, access logs, and API key management coming soon.</p>
          </div>
        )}
      </div>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-3">
      {[...Array(3)].map((_, idx) => (
        <div key={idx} className="h-16 bg-gray-100 rounded-lg" />
      ))}
    </div>
  )
}

function AccountRow({ title, subtitle, status, onDisconnect }: { title: string; subtitle: string; status: string; onDisconnect: () => void }) {
  return (
    <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
      <div>
        <p className="font-medium text-gray-900">{title}</p>
        <p className="text-sm text-gray-500 capitalize">{subtitle}</p>
      </div>
      <div className="flex items-center space-x-3">
        <span className={`text-sm ${status === 'Active' ? 'text-success-600' : 'text-gray-500'}`}>{status}</span>
        <button className="btn-secondary text-sm" onClick={onDisconnect}>Disconnect</button>
      </div>
    </div>
  )
}

function ConnectButton({ label, onClick, loading }: { label: string; onClick: () => void; loading?: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="flex items-center justify-center p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors disabled:opacity-50"
    >
      {loading ? 'Connecting…' : label}
    </button>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
      <EnvelopeIcon className="mx-auto h-12 w-12 text-gray-400" />
      <p className="mt-2 text-sm text-gray-600">{message}</p>
    </div>
  )
}

function ProfileField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input type="text" value={value} readOnly className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50" />
    </div>
  )
}

