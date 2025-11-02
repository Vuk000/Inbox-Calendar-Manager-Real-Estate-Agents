'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { useWebSocket } from '@/lib/websocket';
import { useAuthStore } from '@/lib/stores/authStore';
import { Card } from '@/components/ui/card';
import { useAPI } from '@/lib/hooks/useAPI';
import { analyticsAPI, emailAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { Mail, Calendar, TrendingUp, Eye, MapPin, Activity, Clock } from 'lucide-react';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuth();
  const { accessToken } = useAuthStore();

  // WebSocket for real-time updates
  useWebSocket(accessToken, {
    onNewEmail: (data) => {
      toast.success('New email received!');
    },
    onDraftReady: (data) => {
      toast.success('AI draft ready!');
    },
    onTriageComplete: (data) => {
      toast.success('Email triaged');
    },
    onTaskUpdate: (data) => {
      toast.success('Task updated');
    },
  });

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/signin');
    }
  }, [isAuthenticated, router]);

  const { data: metrics, isLoading } = useAPI(
    ['analytics', 'productivity'],
    () => analyticsAPI.getProductivityMetrics('30d'),
    { enabled: isAuthenticated }
  );

  const { data: emails } = useAPI(
    ['emails', 'unread'],
    () => emailAPI.listEmails({ limit: 5, archived: false }),
    { enabled: isAuthenticated }
  );

  if (!isAuthenticated) {
    return null;
  }

  const stats = [
    {
      label: 'Unread Emails',
      value: emails?.length || metrics?.unread_emails || 0,
      icon: Mail,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      label: 'Upcoming Events',
      value: metrics?.upcoming_events || 0,
      icon: Calendar,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      label: 'Time Saved',
      value: `${metrics?.time_saved_hours || 0}h`,
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      label: 'AI Insights',
      value: metrics?.ai_insights || 0,
      icon: Activity,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  const features = [
    {
      title: 'VisionHome AI',
      description: 'Scan properties with computer vision technology',
      icon: Eye,
      href: '/visionhome',
      gradient: 'from-blue-500 to-indigo-600',
    },
    {
      title: 'Neighborhood Whisper',
      description: 'AI-powered neighborhood fit scores and insights',
      icon: MapPin,
      href: '/neighborhood',
      gradient: 'from-green-500 to-teal-600',
    },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 p-4 md:p-8 md:ml-64">
        <div className="space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
              Welcome back, {user?.full_name || 'User'}!
            </h1>
            <p className="text-gray-600">Here's what's happening with your real estate business</p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <Card key={stat.label} className="p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                      <p className={`text-3xl font-bold ${stat.color}`}>
                        {isLoading ? '...' : stat.value}
                      </p>
                    </div>
                    <div className={`${stat.bgColor} p-3 rounded-lg`}>
                      <Icon className={`w-6 h-6 ${stat.color}`} />
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card
                  key={feature.title}
                  className={`p-6 bg-gradient-to-br ${feature.gradient} text-white cursor-pointer hover:shadow-xl transition-all duration-300 hover:scale-105`}
                  onClick={() => router.push(feature.href)}
                >
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-white/20 rounded-lg backdrop-blur-sm">
                      <Icon className="w-8 h-8" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                      <p className="text-white/90">{feature.description}</p>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          {/* Recent Activity */}
          <Card className="p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Emails</h2>
            {isLoading ? (
              <div className="text-center py-8 text-gray-500">Loading...</div>
            ) : emails && emails.length > 0 ? (
              <div className="space-y-4">
                {emails.slice(0, 5).map((email: any) => (
                  <div key={email.id} className="flex items-start gap-4 p-4 hover:bg-gray-50 rounded-lg transition-colors">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <Mail className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">{email.sender || 'Unknown'}</p>
                      <p className="text-sm text-gray-600 truncate">{email.subject || 'No subject'}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">No recent emails</div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
