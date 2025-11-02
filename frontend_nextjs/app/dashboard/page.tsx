'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { useWebSocket } from '@/lib/websocket';
import { useAuthStore } from '@/lib/stores/authStore';
import { Card } from '@/components/ui/card';
import { HolographicCard } from '@/components/cyberpunk/HolographicCard';
import { ScrollReveal } from '@/components/cyberpunk/ScrollReveal';
import { NeonText } from '@/components/cyberpunk/NeonText';
import { motion } from 'framer-motion';
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
      glowColor: 'blue' as const,
    },
    {
      label: 'Upcoming Events',
      value: metrics?.upcoming_events || 0,
      icon: Calendar,
      glowColor: 'purple' as const,
    },
    {
      label: 'Time Saved',
      value: `${metrics?.time_saved_hours || 0}h`,
      icon: Clock,
      glowColor: 'pink' as const,
    },
    {
      label: 'AI Insights',
      value: metrics?.ai_insights || 0,
      icon: Activity,
      glowColor: 'blue' as const,
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
    <div className="flex min-h-screen bg-dark-bg">
      <Sidebar />
      <div className="flex-1 p-4 md:p-8 md:ml-64">
        <div className="space-y-8">
          {/* Header */}
          <ScrollReveal>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold mb-2 font-orbitron">
                <NeonText color="blue">Welcome back, {user?.full_name || 'User'}!</NeonText>
              </h1>
              <p className="text-gray-400">Here's what's happening with your real estate business</p>
            </div>
          </ScrollReveal>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <ScrollReveal key={stat.label} delay={index * 0.1}>
                  <HolographicCard glowColor={stat.glowColor} className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400 mb-1">{stat.label}</p>
                        <p className="text-3xl font-bold text-neon-cyan font-orbitron">
                          {isLoading ? '...' : stat.value}
                        </p>
                      </div>
                      <div className="bg-neon-cyan/20 p-3 rounded-lg border border-neon-cyan/30">
                        <Icon className="w-6 h-6 text-neon-cyan" />
                      </div>
                    </div>
                  </HolographicCard>
                </ScrollReveal>
              );
            })}
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <ScrollReveal key={feature.title} delay={index * 0.2}>
                  <motion.div
                    whileHover={{ scale: 1.05, y: -5 }}
                    transition={{ duration: 0.2 }}
                  >
                    <HolographicCard
                      glowColor={index === 0 ? 'blue' : 'purple'}
                      className="p-6 cursor-pointer bg-gradient-to-br from-neon-cyan/20 to-neon-purple/20"
                      onClick={() => router.push(feature.href)}
                    >
                      <div className="flex items-start gap-4">
                        <div className="p-3 bg-neon-cyan/20 rounded-lg backdrop-blur-sm border border-neon-cyan/30">
                          <Icon className="w-8 h-8 text-neon-cyan" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-xl font-bold mb-2 text-gray-100 font-orbitron">{feature.title}</h3>
                          <p className="text-gray-300">{feature.description}</p>
                        </div>
                      </div>
                    </HolographicCard>
                  </motion.div>
                </ScrollReveal>
              );
            })}
          </div>

          {/* Recent Activity */}
          <ScrollReveal delay={0.3}>
            <HolographicCard glowColor="blue" className="p-6">
              <h2 className="text-xl font-bold mb-4 text-gray-100 font-orbitron">
                <NeonText color="blue">Recent Emails</NeonText>
              </h2>
              {isLoading ? (
                <div className="text-center py-8 text-gray-400">Loading...</div>
              ) : emails && emails.length > 0 ? (
                <div className="space-y-4">
                  {emails.slice(0, 5).map((email: any) => (
                    <motion.div
                      key={email.id}
                      className="flex items-start gap-4 p-4 hover:bg-neon-cyan/10 rounded-lg transition-colors border border-neon-cyan/10"
                      whileHover={{ x: 4 }}
                    >
                      <div className="w-10 h-10 bg-neon-cyan/20 rounded-full flex items-center justify-center flex-shrink-0 border border-neon-cyan/30">
                        <Mail className="w-5 h-5 text-neon-cyan" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-100 truncate">{email.sender || 'Unknown'}</p>
                        <p className="text-sm text-gray-400 truncate">{email.subject || 'No subject'}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">No recent emails</div>
              )}
            </HolographicCard>
          </ScrollReveal>
        </div>
      </div>
    </div>
  );
}
