'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { useAPI } from '@/lib/hooks/useAPI';
import { analyticsAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { TrendingUp, Mail, Calendar, Sparkles, Download, Filter } from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { LineChartComponent, BarChartComponent, AreaChartComponent, PieChartComponent, AnimatedCounter } from '@/components/ui/charts';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export default function AnalyticsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [timeframe, setTimeframe] = useState('30d');
  const [metricType, setMetricType] = useState('productivity');

  const { data: metrics, isLoading } = useAPI(
    ['analytics', 'productivity', timeframe],
    () => analyticsAPI.getProductivityMetrics(timeframe),
    { enabled: isAuthenticated }
  );

  if (!isAuthenticated) {
    router.push('/');
    return null;
  }

  // Transform backend data for charts
  const defaultEmailActivity = [
    { name: 'Mon', emails: 0, responses: 0 },
    { name: 'Tue', emails: 0, responses: 0 },
    { name: 'Wed', emails: 0, responses: 0 },
    { name: 'Thu', emails: 0, responses: 0 },
    { name: 'Fri', emails: 0, responses: 0 },
    { name: 'Sat', emails: 0, responses: 0 },
    { name: 'Sun', emails: 0, responses: 0 },
  ];

  const emailActivityData = metrics?.email_activity?.map((item: any) => ({
    name: new Date(item.date).toLocaleDateString('en-US', { weekday: 'short' }),
    emails: item.emails || 0,
    responses: item.ai_actions || 0,
  })) || defaultEmailActivity;

  const leadFunnelData = metrics?.lead_funnel?.map((item: any) => ({
    name: item.stage,
    value: item.count || 0,
  })) || [
    { name: 'New', value: 0 },
    { name: 'Contacted', value: 0 },
    { name: 'Qualified', value: 0 },
  ];

  const defaultTimeSaved = [
    { name: 'Week 1', saved: 0 },
    { name: 'Week 2', saved: 0 },
    { name: 'Week 3', saved: 0 },
    { name: 'Week 4', saved: 0 },
  ];

  const timeSavedData = metrics?.roi_over_time?.map((item: any, index: number) => ({
    name: `Week ${index + 1}`,
    saved: item.hours_saved || 0,
  })) || defaultTimeSaved;

  const defaultSourceData = [
    { name: 'Email Triage', value: 0 },
    { name: 'Drafts', value: 0 },
    { name: 'Tasks Created', value: 0 },
  ];

  const sourceData = metrics?.ai_action_breakdown?.map((item: any) => ({
    name: item.name,
    value: item.value || 0,
  })) || defaultSourceData;

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
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-orbitron font-bold text-transparent bg-clip-text bg-gradient-neon mb-2">
                Analytics
              </h1>
              <p className="text-gray-400">Track your productivity and insights</p>
            </div>
            <div className="flex gap-4">
              <Select
                options={[
                  { value: '7d', label: 'Last 7 days' },
                  { value: '30d', label: 'Last 30 days' },
                  { value: '90d', label: 'Last 90 days' },
                  { value: '1y', label: 'Last year' },
                ]}
                value={timeframe}
                onChange={(value) => setTimeframe(value)}
                placeholder="Select timeframe"
              />
              <Button variant="secondary">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <Mail className="w-8 h-8 text-neon-cyan" />
                <Badge variant="success">+12%</Badge>
              </div>
              <p className="text-sm text-gray-400 mb-1">Total Emails</p>
              <AnimatedCounter
                value={metrics?.emails_processed_today || 0}
                className="text-3xl font-orbitron font-bold text-neon-cyan"
              />
            </Card>
            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <Calendar className="w-8 h-8 text-neon-pink" />
                <Badge variant="success">+8%</Badge>
              </div>
              <p className="text-sm text-gray-400 mb-1">Events Created</p>
              <AnimatedCounter
                value={metrics?.tasks_completed || 0}
                className="text-3xl font-orbitron font-bold text-neon-pink"
              />
            </Card>
            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <Sparkles className="w-8 h-8 text-neon-purple" />
                <Badge variant="info">AI</Badge>
              </div>
              <p className="text-sm text-gray-400 mb-1">AI Actions</p>
              <AnimatedCounter
                value={metrics?.drafts_generated || 0}
                className="text-3xl font-orbitron font-bold text-neon-purple"
              />
            </Card>
            <Card className="p-6">
              <div className="flex items-center justify-between mb-2">
                <TrendingUp className="w-8 h-8 text-green-400" />
                <Badge variant="neon">Best</Badge>
              </div>
              <p className="text-sm text-gray-400 mb-1">Time Saved</p>
              <AnimatedCounter
                value={metrics?.time_saved_hours || 53}
                suffix="h"
                className="text-3xl font-orbitron font-bold text-green-400"
              />
            </Card>
          </div>

          {/* Tabs for different views */}
          <Tabs defaultValue="overview">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="productivity">Productivity</TabsTrigger>
              <TabsTrigger value="leads">Leads</TabsTrigger>
              <TabsTrigger value="insights">AI Insights</TabsTrigger>
            </TabsList>

            <TabsContent value="overview">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                <AreaChartComponent
                  data={emailActivityData}
                  title="Email Activity"
                  className="p-6"
                />
                <BarChartComponent
                  data={timeSavedData}
                  title="Time Saved Per Week"
                  className="p-6"
                />
                <PieChartComponent
                  data={leadFunnelData}
                  title="Lead Funnel"
                  className="p-6"
                />
                <PieChartComponent
                  data={sourceData}
                  title="Lead Sources"
                  className="p-6"
                />
              </div>
            </TabsContent>

            <TabsContent value="productivity">
              <div className="grid grid-cols-1 gap-6 mt-6">
                <LineChartComponent
                  data={emailActivityData}
                  title="Email Productivity Trends"
                  className="p-6"
                />
                <BarChartComponent
                  data={timeSavedData}
                  title="Time Saved Breakdown"
                  className="p-6"
                />
              </div>
            </TabsContent>

            <TabsContent value="leads">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                <PieChartComponent
                  data={leadFunnelData}
                  title="Lead Conversion Funnel"
                  className="p-6"
                />
                <BarChartComponent
                  data={sourceData.map((s) => ({ name: s.name, leads: s.value }))}
                  title="Leads by Source"
                  className="p-6"
                />
              </div>
            </TabsContent>

                <TabsContent value="insights">
                  <Card className="p-6 mt-6">
                    <h3 className="text-xl font-orbitron text-neon-cyan mb-4">AI-Generated Insights</h3>
                    <div className="space-y-4">
                      {metrics?.urgent_emails?.length > 0 ? (
                        metrics.urgent_emails.map((email: any, index: number) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="p-4 bg-neon-cyan/10 rounded-lg border border-neon-cyan/20"
                          >
                            <p className="text-gray-300 font-semibold">{email.subject}</p>
                            <p className="text-sm text-gray-400 mt-1">From: {email.sender}</p>
                            <p className="text-sm text-neon-pink mt-1">Urgency: {email.urgency_score}%</p>
                          </motion.div>
                        ))
                      ) : (
                        <p className="text-gray-400">No urgent emails or insights available yet</p>
                      )}
                    </div>
                  </Card>
                </TabsContent>
          </Tabs>
        </motion.div>
      </div>
    </div>
  );
}
