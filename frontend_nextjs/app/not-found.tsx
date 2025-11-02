'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { Home, AlertCircle, WifiOff } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface ErrorPageProps {
  statusCode: number;
  title: string;
  message: string;
  action?: ReactNode;
}

function ErrorPage({ statusCode, title, message, action }: ErrorPageProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full text-center"
      >
        <Card className="p-8">
          <motion.div
            initial={{ y: -20 }}
            animate={{ y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-6"
          >
            <div className="text-8xl font-orbitron font-bold text-transparent bg-clip-text bg-gradient-neon mb-4">
              {statusCode}
            </div>
            <h1 className="text-3xl font-orbitron font-bold text-neon-cyan mb-2">
              {title}
            </h1>
            <p className="text-gray-400 mb-8">{message}</p>
          </motion.div>
          
          {action || (
            <Link href="/dashboard">
              <Button variant="primary" className="w-full">
                <Home className="w-4 h-4 mr-2" />
                Go Home
              </Button>
            </Link>
          )}
        </Card>
      </motion.div>
    </div>
  );
}

export default function NotFound() {
  return (
    <ErrorPage
      statusCode={404}
      title="Page Not Found"
      message="The page you're looking for doesn't exist or has been moved."
    />
  );
}

export function ErrorBoundaryFallback({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full"
      >
        <Card className="p-8">
          <div className="text-center mb-6">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-orbitron font-bold text-red-400 mb-2">
              Something went wrong
            </h1>
            <p className="text-gray-400 mb-4">{error.message}</p>
          </div>
          
          <div className="space-y-3">
            <Button
              variant="primary"
              onClick={resetErrorBoundary}
              className="w-full"
            >
              Try Again
            </Button>
            <Link href="/dashboard" className="block">
              <Button variant="secondary" className="w-full">
                <Home className="w-4 h-4 mr-2" />
                Go Home
              </Button>
            </Link>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}

export function ServerError() {
  return (
    <ErrorPage
      statusCode={500}
      title="Server Error"
      message="Something went wrong on our end. Please try again later."
      action={
        <Button variant="primary" onClick={() => window.location.reload()} className="w-full">
          Reload Page
        </Button>
      }
    />
  );
}

export function NetworkError() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full text-center"
      >
        <Card className="p-8">
          <WifiOff className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h1 className="text-2xl font-orbitron font-bold text-yellow-400 mb-2">
            Connection Lost
          </h1>
          <p className="text-gray-400 mb-8">
            Please check your internet connection and try again.
          </p>
          <Button variant="primary" onClick={() => window.location.reload()} className="w-full">
            Retry Connection
          </Button>
        </Card>
      </motion.div>
    </div>
  );
}

