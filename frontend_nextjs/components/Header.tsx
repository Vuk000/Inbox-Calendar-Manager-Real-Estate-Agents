'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Sparkles, Menu, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/inbox', label: 'Inbox' },
    { href: '/calendar', label: 'Calendar' },
    { href: '/analytics', label: 'Analytics' },
    { href: '/visionhome', label: 'VisionHome' },
    { href: '/neighborhood', label: 'Neighborhood' },
  ];

  return (
    <motion.header 
      className="sticky top-0 z-50 glass-effect border-b border-neon-cyan/20 bg-dark-bg/80 backdrop-blur-md"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <motion.div
              whileHover={{ scale: 1.2, rotate: 360 }}
              transition={{ duration: 0.5 }}
            >
              <Sparkles className="w-8 h-8 text-neon-cyan group-hover:text-neon-pink transition-colors drop-shadow-[0_0_10px_#00FFFF]" />
            </motion.div>
            <span className="text-xl font-orbitron font-bold text-transparent bg-clip-text bg-gradient-neon neon-glow">
              RealInbox AI Pro
            </span>
          </Link>

          {isAuthenticated ? (
            <>
            <nav className="hidden md:flex items-center gap-6" role="navigation" aria-label="Main navigation">
              {navLinks.map((link) => (
                <motion.div
                  key={link.href}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Link
                    href={link.href}
                    className="text-gray-300 hover:text-neon-cyan transition-colors font-medium relative group px-2 py-1"
                    aria-label={`Navigate to ${link.label}`}
                  >
                    {link.label}
                    <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-neon-cyan group-hover:w-full transition-all duration-300 shadow-[0_0_10px_#00FFFF]" />
                    <span className="absolute inset-0 bg-neon-cyan/10 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm" />
                  </Link>
                </motion.div>
              ))}
            </nav>

              <div className="hidden md:flex items-center gap-4">
                <span className="text-sm text-gray-400">{user?.full_name}</span>
                <motion.button
                  onClick={logout}
                  className="px-4 py-2 border border-neon-cyan/30 rounded-lg hover:border-neon-cyan transition-colors neon-border hover:shadow-neon-glow-blue"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Logout
                </motion.button>
              </div>

              <button
                className="md:hidden text-neon-cyan"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                aria-label="Toggle mobile menu"
                aria-expanded={isMobileMenuOpen}
              >
                {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </>
          ) : (
            <Link
              href="/"
              className="px-4 py-2 border border-neon-cyan/30 rounded-lg hover:border-neon-cyan transition-colors"
            >
              Sign In
            </Link>
          )}
        </div>

        {isMobileMenuOpen && isAuthenticated && (
          <motion.nav
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden mt-4 space-y-2"
          >
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="block py-2 text-gray-300 hover:text-neon-cyan transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <button
              onClick={() => {
                logout();
                setIsMobileMenuOpen(false);
              }}
              className="block w-full text-left py-2 text-gray-300 hover:text-neon-cyan transition-colors"
            >
              Logout
            </button>
          </motion.nav>
        )}
      </div>
    </header>
  );
}

