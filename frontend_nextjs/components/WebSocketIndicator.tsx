'use client';

import { useEffect, useState } from 'react';
import { useWebSocket } from '@/lib/websocket';
import { useAuthStore } from '@/lib/stores/authStore';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Mail, Sparkles, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export function WebSocketConnectionIndicator() {
  const { accessToken } = useAuthStore();
  const [notifications, setNotifications] = useState<any[]>([]);

  const { connected } = useWebSocket(accessToken, {
    onNewEmail: (data) => {
      toast.success('New email received!');
      setNotifications((prev) => [...prev, { type: 'email', data, timestamp: new Date() }]);
    },
    onDraftReady: (data) => {
      toast.success('AI draft ready!');
      setNotifications((prev) => [...prev, { type: 'draft', data, timestamp: new Date() }]);
    },
    onTriageComplete: (data) => {
      toast.success('Email triaged');
      setNotifications((prev) => [...prev, { type: 'triage', data, timestamp: new Date() }]);
    },
    onTaskUpdate: (data) => {
      toast.success('Task updated');
      setNotifications((prev) => [...prev, { type: 'task', data, timestamp: new Date() }]);
    },
    onConnected: () => {
      console.log('WebSocket connected');
    },
    onDisconnected: () => {
      console.log('WebSocket disconnected');
    },
  });

  return (
    <motion.div
      className="fixed bottom-4 right-4 z-50"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card className={`p-3 flex items-center gap-2 ${connected ? 'border-neon-cyan' : 'border-gray-600'}`}>
        <div className={`w-2 h-2 rounded-full ${connected ? 'bg-neon-cyan animate-pulse' : 'bg-gray-500'}`} />
        <span className="text-sm text-gray-400">
          {connected ? 'Connected' : 'Disconnected'}
        </span>
      </Card>
    </motion.div>
  );
}

