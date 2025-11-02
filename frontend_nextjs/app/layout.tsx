'use client';

import { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import WebGLBackground from '@/components/WebGLBackground';
import { Footer } from '@/components/Footer';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { WebSocketConnectionIndicator } from '@/components/WebSocketIndicator';
import { Orbitron, Inter } from 'next/font/google';
import { PageTransition } from '@/components/ui/micro-interactions';
import { CommandPalette, useCommandPalette } from '@/components/ui/command-palette';
import './globals.css';

const orbitron = Orbitron({
  subsets: ['latin'],
  variable: '--font-orbitron',
  display: 'swap',
});

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

function LayoutContent({ children }: { children: ReactNode }) {
  const commandPalette = useCommandPalette();
  const pathname = usePathname();
  const isAuthPage = pathname === '/signin' || pathname === '/signup';
  const isLandingPage = pathname === '/';

  return (
    <>
      {!isAuthPage && !isLandingPage && <WebGLBackground />}
      {!isAuthPage && !isLandingPage && <Header />}
      <PageTransition>
        <main className="min-h-screen">
          {children}
        </main>
      </PageTransition>
      {!isAuthPage && !isLandingPage && <Footer />}
      {!isAuthPage && <WebSocketConnectionIndicator />}
      {!isAuthPage && (
        <CommandPalette
          isOpen={commandPalette.isOpen}
          onClose={commandPalette.close}
          commands={commandPalette.commands}
        />
      )}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: isAuthPage || isLandingPage ? '#fff' : '#1A0033',
            color: isAuthPage || isLandingPage ? '#111827' : '#00FFFF',
            border: isAuthPage || isLandingPage ? '1px solid #e5e7eb' : '1px solid #00FFFF',
            boxShadow: isAuthPage || isLandingPage 
              ? '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
              : '0 0 10px rgba(0, 255, 255, 0.5)',
          },
          success: {
            iconTheme: {
              primary: isAuthPage || isLandingPage ? '#10b981' : '#00FFFF',
              secondary: isAuthPage || isLandingPage ? '#fff' : '#1A0033',
            },
          },
          error: {
            iconTheme: {
              primary: isAuthPage || isLandingPage ? '#ef4444' : '#FF00FF',
              secondary: isAuthPage || isLandingPage ? '#fff' : '#1A0033',
            },
          },
          loading: {
            iconTheme: {
              primary: isAuthPage || isLandingPage ? '#3b82f6' : '#00FFFF',
              secondary: isAuthPage || isLandingPage ? '#fff' : '#1A0033',
            },
          },
        }}
      />
    </>
  );
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`${orbitron.variable} ${inter.variable} dark`}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="RealInbox AI Pro - AI-powered inbox and calendar management for real estate teams" />
        <title>RealInbox AI Pro</title>
      </head>
      <body className="font-inter antialiased">
        <ErrorBoundary>
          <QueryClientProvider client={queryClient}>
            <LayoutContent>{children}</LayoutContent>
          </QueryClientProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
