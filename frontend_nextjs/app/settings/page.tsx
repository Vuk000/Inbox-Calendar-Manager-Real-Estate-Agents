'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Sidebar } from '@/components/Sidebar';
import { Settings, User, Bell, Shield, Key, Palette, Globe, Mail } from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { toast } from 'react-hot-toast';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { userAPI } from '@/lib/api';

export default function SettingsPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  const { data: userData, isLoading } = useAPI(
    ['user', 'profile'],
    () => userAPI.getProfile(),
    { enabled: isAuthenticated }
  );

  const updateProfileMutation = useAPIMutation(
    (data: any) => userAPI.updateProfile(data),
    {
      onSuccess: () => {
        toast.success('Profile updated successfully');
      },
    }
  );

  const updatePreferencesMutation = useAPIMutation(
    (data: any) => userAPI.updatePreferences(data),
    {
      onSuccess: () => {
        toast.success('Preferences updated');
      },
    }
  );

  if (!isAuthenticated) {
    router.push('/');
    return null;
  }

  const handleProfileSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    updateProfileMutation.mutate({
      full_name: formData.get('full_name'),
      email: formData.get('email'),
      phone: formData.get('phone'),
    });
  };

  const handlePreferencesSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    updatePreferencesMutation.mutate({
      theme: formData.get('theme'),
      notifications_enabled: formData.get('notifications_enabled') === 'on',
      email_notifications: formData.get('email_notifications') === 'on',
      language: formData.get('language'),
    });
  };

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
              Settings
            </h1>
            <p className="text-gray-400">Manage your account and preferences</p>
          </div>

          <Tabs defaultValue="profile">
            <TabsList>
              <TabsTrigger value="profile">
                <User className="w-4 h-4 mr-2" />
                Profile
              </TabsTrigger>
              <TabsTrigger value="notifications">
                <Bell className="w-4 h-4 mr-2" />
                Notifications
              </TabsTrigger>
              <TabsTrigger value="security">
                <Shield className="w-4 h-4 mr-2" />
                Security
              </TabsTrigger>
              <TabsTrigger value="appearance">
                <Palette className="w-4 h-4 mr-2" />
                Appearance
              </TabsTrigger>
              <TabsTrigger value="integrations">
                <Globe className="w-4 h-4 mr-2" />
                Integrations
              </TabsTrigger>
            </TabsList>

            <TabsContent value="profile">
              <Card className="p-6">
                <h2 className="text-2xl font-orbitron text-neon-cyan mb-4">Profile Information</h2>
                <form onSubmit={handleProfileSubmit} className="space-y-4">
                  <Input
                    name="full_name"
                    label="Full Name"
                    defaultValue={userData?.full_name || user?.email || ''}
                    placeholder="Enter your full name"
                  />
                  <Input
                    name="email"
                    label="Email"
                    type="email"
                    defaultValue={userData?.email || user?.email || ''}
                    placeholder="Enter your email"
                  />
                  <Input
                    name="phone"
                    label="Phone"
                    mask="phone"
                    defaultValue={userData?.phone || ''}
                    placeholder="Enter your phone number"
                  />
                  <div className="flex justify-end">
                    <Button type="submit" variant="primary">
                      Save Changes
                    </Button>
                  </div>
                </form>
              </Card>
            </TabsContent>

            <TabsContent value="notifications">
              <Card className="p-6">
                <h2 className="text-2xl font-orbitron text-neon-cyan mb-4">Notification Preferences</h2>
                <form onSubmit={handlePreferencesSubmit} className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-dark-purple/50 rounded-lg border border-neon-cyan/20">
                    <div>
                      <h3 className="font-medium text-white">Push Notifications</h3>
                      <p className="text-sm text-gray-400">Receive browser notifications</p>
                    </div>
                    <input
                      type="checkbox"
                      name="notifications_enabled"
                      defaultChecked={userData?.preferences?.notifications_enabled}
                      className="w-5 h-5 text-neon-cyan bg-dark-purple border-neon-cyan/30 rounded focus:ring-neon-cyan"
                    />
                  </div>
                  <div className="flex items-center justify-between p-4 bg-dark-purple/50 rounded-lg border border-neon-cyan/20">
                    <div>
                      <h3 className="font-medium text-white">Email Notifications</h3>
                      <p className="text-sm text-gray-400">Receive notifications via email</p>
                    </div>
                    <input
                      type="checkbox"
                      name="email_notifications"
                      defaultChecked={userData?.preferences?.email_notifications}
                      className="w-5 h-5 text-neon-cyan bg-dark-purple border-neon-cyan/30 rounded focus:ring-neon-cyan"
                    />
                  </div>
                  <div className="flex justify-end">
                    <Button type="submit" variant="primary">
                      Save Preferences
                    </Button>
                  </div>
                </form>
              </Card>
            </TabsContent>

            <TabsContent value="security">
              <Card className="p-6">
                <h2 className="text-2xl font-orbitron text-neon-cyan mb-4">Security Settings</h2>
                <div className="space-y-4">
                  <div className="p-4 bg-dark-purple/50 rounded-lg border border-neon-cyan/20">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-white">Change Password</h3>
                      <Key className="w-5 h-5 text-neon-cyan" />
                    </div>
                    <p className="text-sm text-gray-400 mb-4">
                      Update your password to keep your account secure
                    </p>
                    <Button variant="secondary">
                      Change Password
                    </Button>
                  </div>
                  <div className="p-4 bg-dark-purple/50 rounded-lg border border-neon-cyan/20">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-white">Two-Factor Authentication</h3>
                      <Shield className="w-5 h-5 text-neon-cyan" />
                    </div>
                    <p className="text-sm text-gray-400 mb-4">
                      Add an extra layer of security to your account
                    </p>
                    <Button variant="secondary">
                      Enable 2FA
                    </Button>
                  </div>
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="appearance">
              <Card className="p-6">
                <h2 className="text-2xl font-orbitron text-neon-cyan mb-4">Appearance</h2>
                <form onSubmit={handlePreferencesSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-neon-cyan mb-2">
                      Theme
                    </label>
                    <Select
                      options={[
                        { value: 'dark', label: 'Dark' },
                        { value: 'light', label: 'Light' },
                        { value: 'auto', label: 'Auto' },
                      ]}
                      value={userData?.preferences?.theme || 'dark'}
                      onChange={(value) => {
                        updatePreferencesMutation.mutate({ theme: value });
                      }}
                      placeholder="Select theme"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neon-cyan mb-2">
                      Language
                    </label>
                    <Select
                      options={[
                        { value: 'en', label: 'English' },
                        { value: 'es', label: 'Spanish' },
                        { value: 'fr', label: 'French' },
                      ]}
                      value={userData?.preferences?.language || 'en'}
                      onChange={(value) => {
                        updatePreferencesMutation.mutate({ language: value });
                      }}
                      placeholder="Select language"
                    />
                  </div>
                </form>
              </Card>
            </TabsContent>

            <TabsContent value="integrations">
              <Card className="p-6">
                <h2 className="text-2xl font-orbitron text-neon-cyan mb-4">Integrations</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-dark-purple/50 rounded-lg border border-neon-cyan/20">
                    <div className="flex items-center gap-3">
                      <Mail className="w-5 h-5 text-neon-cyan" />
                      <div>
                        <h3 className="font-medium text-white">Email Integration</h3>
                        <p className="text-sm text-gray-400">Connect your email account</p>
                      </div>
                    </div>
                    <Button variant="secondary">
                      Connect
                    </Button>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-dark-purple/50 rounded-lg border border-neon-cyan/20">
                    <div className="flex items-center gap-3">
                      <Globe className="w-5 h-5 text-neon-cyan" />
                      <div>
                        <h3 className="font-medium text-white">Calendar Integration</h3>
                        <p className="text-sm text-gray-400">Sync with Google Calendar</p>
                      </div>
                    </div>
                    <Button variant="secondary">
                      Connect
                    </Button>
                  </div>
                </div>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>
      </div>
    </div>
  );
}

