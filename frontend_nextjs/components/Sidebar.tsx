'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Mail,
  Calendar,
  BarChart3,
  Camera,
  MapPin,
  ChevronLeft,
  ChevronRight,
  Settings,
  Menu,
  X,
  FileText,
  CheckSquare,
  User,
  Sparkles,
  Users,
  Building2,
  Home,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/lib/hooks/useAuth';
import { Drawer } from '@/components/ui/drawer';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/inbox', label: 'Inbox', icon: Mail },
  { href: '/calendar', label: 'Calendar', icon: Calendar },
  { href: '/analytics', label: 'Analytics', icon: BarChart3 },
  { href: '/visionhome', label: 'VisionHome', icon: Camera },
  { href: '/neighborhood', label: 'Neighborhood', icon: MapPin },
  { href: '/drafts', label: 'Drafts', icon: FileText },
  { href: '/tasks', label: 'Tasks', icon: CheckSquare },
  { href: '/contacts', label: 'Contacts', icon: User },
  { href: '/properties', label: 'Properties', icon: Home },
  { href: '/transactions', label: 'Transactions', icon: Building2 },
  { href: '/teams', label: 'Teams', icon: Users },
  { href: '/ai-actions', label: 'AI Actions', icon: Sparkles },
  { href: '/integrations', label: 'Integrations', icon: Settings },
  { href: '/settings', label: 'Settings', icon: Settings },
  { href: '/subscription', label: 'Subscription', icon: Settings },
];

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileOpen(false);
  }, [pathname]);

  // Close mobile menu on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsMobileOpen(false);
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const SidebarContent = ({ onItemClick }: { onItemClick?: () => void }) => (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-neon-cyan/20 mb-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-orbitron font-bold text-transparent bg-clip-text bg-gradient-neon">
            RealInbox AI Pro
          </h2>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden md:block p-1 bg-dark-purple border border-neon-cyan rounded-full hover:bg-neon-cyan/10 transition-colors"
            aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4 text-neon-cyan" />
            ) : (
              <ChevronLeft className="w-4 h-4 text-neon-cyan" />
            )}
          </button>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-2 overflow-y-auto" role="navigation" aria-label="Sidebar navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onItemClick}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300',
                'hover:bg-neon-cyan/10 hover:text-neon-cyan focus:outline-none focus:ring-2 focus:ring-neon-cyan',
                'touch-manipulation', // Better touch targets
                isActive
                  ? 'bg-neon-cyan/20 text-neon-cyan border-l-2 border-neon-cyan'
                  : 'text-gray-400'
              )}
              aria-label={item.label}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
              {(!isCollapsed || isMobileOpen) && (
                <span className="font-medium">{item.label}</span>
              )}
            </Link>
          );
        })}
      </nav>
    </div>
  );

  if (!isAuthenticated) return null;

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-dark-purple/80 backdrop-blur-sm border border-neon-cyan/20 rounded-lg hover:bg-neon-cyan/10 transition-colors"
        aria-label="Open menu"
        aria-expanded={isMobileOpen}
      >
        <Menu className="w-6 h-6 text-neon-cyan" />
      </button>

      {/* Desktop Sidebar */}
      <motion.aside
        className={cn(
          'fixed left-0 top-0 h-screen bg-dark-purple/80 backdrop-blur-sm border-r border-neon-cyan/20',
          'transition-all duration-300 z-40',
          'hidden md:block', // Hide on mobile, show on desktop
          isCollapsed ? 'w-16' : 'w-64'
        )}
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <SidebarContent />
      </motion.aside>

      {/* Mobile Drawer */}
      <Drawer
        isOpen={isMobileOpen}
        onClose={() => setIsMobileOpen(false)}
        position="left"
        size="sm"
      >
        <div className="relative h-full">
          <button
            onClick={() => setIsMobileOpen(false)}
            className="absolute top-4 right-4 p-2 text-gray-400 hover:text-neon-cyan transition-colors"
            aria-label="Close menu"
          >
            <X className="w-6 h-6" />
          </button>
          <SidebarContent onItemClick={() => setIsMobileOpen(false)} />
        </div>
      </Drawer>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsMobileOpen(false)}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 md:hidden"
            aria-hidden="true"
          />
        )}
      </AnimatePresence>
    </>
  );
}
