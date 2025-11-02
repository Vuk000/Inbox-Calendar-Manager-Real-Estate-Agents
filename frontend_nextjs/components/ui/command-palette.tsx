'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Command, X, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Card } from './card';

interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon?: React.ReactNode;
  action: () => void;
  category: string;
  keywords?: string[];
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  commands: CommandItem[];
}

export function CommandPalette({ isOpen, onClose, commands }: CommandPaletteProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const router = useRouter();

  const filteredCommands = commands.filter((cmd) => {
    const query = searchQuery.toLowerCase();
    return (
      cmd.label.toLowerCase().includes(query) ||
      cmd.description?.toLowerCase().includes(query) ||
      cmd.keywords?.some((k) => k.toLowerCase().includes(query)) ||
      cmd.category.toLowerCase().includes(query)
    );
  });

  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) acc[cmd.category] = [];
    acc[cmd.category].push(cmd);
    return acc;
  }, {} as Record<string, CommandItem[]>);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, filteredCommands.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        const selectedCommand = filteredCommands[selectedIndex];
        if (selectedCommand) {
          selectedCommand.action();
          onClose();
        }
      } else if (e.key === 'Escape') {
        onClose();
      }
    },
    [isOpen, filteredCommands, selectedIndex, onClose]
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, handleKeyDown]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [searchQuery]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] px-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -20 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-2xl"
        >
          <Card className="p-0 overflow-hidden border-2 border-neon-cyan shadow-neon-cyan">
            {/* Search Input */}
            <div className="flex items-center gap-3 p-4 border-b border-neon-cyan/20">
              <Search className="w-5 h-5 text-neon-cyan flex-shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Type a command or search..."
                className="flex-1 bg-transparent text-white placeholder:text-gray-500 focus:outline-none"
                autoFocus
              />
              <kbd className="px-2 py-1 text-xs bg-dark-purple border border-neon-cyan/30 rounded text-gray-400">
                ESC
              </kbd>
            </div>

            {/* Command List */}
            <div className="max-h-96 overflow-y-auto">
              {filteredCommands.length === 0 ? (
                <div className="p-8 text-center text-gray-400">
                  <p>No commands found</p>
                  <p className="text-sm mt-2">Try a different search term</p>
                </div>
              ) : (
                Object.entries(groupedCommands).map(([category, categoryCommands]) => (
                  <div key={category}>
                    <div className="px-4 py-2 text-xs font-orbitron text-neon-cyan/70 uppercase sticky top-0 bg-dark-purple/80 backdrop-blur-sm">
                      {category}
                    </div>
                    {categoryCommands.map((cmd, index) => {
                      const globalIndex = filteredCommands.indexOf(cmd);
                      const isSelected = globalIndex === selectedIndex;

                      return (
                        <motion.button
                          key={cmd.id}
                          onClick={() => {
                            cmd.action();
                            onClose();
                          }}
                          className={cn(
                            'w-full px-4 py-3 text-left flex items-center gap-3 transition-colors',
                            isSelected && 'bg-neon-cyan/20 text-neon-cyan',
                            !isSelected && 'text-gray-300 hover:bg-neon-cyan/10'
                          )}
                          onMouseEnter={() => setSelectedIndex(globalIndex)}
                        >
                          {cmd.icon && <span className="flex-shrink-0">{cmd.icon}</span>}
                          <div className="flex-1 min-w-0">
                            <p className="font-medium truncate">{cmd.label}</p>
                            {cmd.description && (
                              <p className="text-sm text-gray-400 truncate">{cmd.description}</p>
                            )}
                          </div>
                          {isSelected && (
                            <motion.div
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                            >
                              <ArrowRight className="w-4 h-4" />
                            </motion.div>
                          )}
                        </motion.button>
                      );
                    })}
                  </div>
                ))
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 border-t border-neon-cyan/20 flex items-center justify-between text-xs text-gray-400">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1">
                  <kbd className="px-1.5 py-0.5 bg-dark-purple border border-neon-cyan/30 rounded">↑</kbd>
                  <kbd className="px-1.5 py-0.5 bg-dark-purple border border-neon-cyan/30 rounded">↓</kbd>
                  <span>Navigate</span>
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="px-1.5 py-0.5 bg-dark-purple border border-neon-cyan/30 rounded">Enter</kbd>
                  <span>Select</span>
                </span>
              </div>
              <span>{filteredCommands.length} commands</span>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// Hook to use Command Palette
export function useCommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();

  const toggle = useCallback(() => setIsOpen((prev) => !prev), []);
  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        toggle();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [toggle]);

  const defaultCommands: CommandItem[] = [
    {
      id: 'dashboard',
      label: 'Go to Dashboard',
      description: 'Navigate to dashboard',
      category: 'Navigation',
      action: () => router.push('/dashboard'),
      keywords: ['home', 'main'],
    },
    {
      id: 'inbox',
      label: 'Open Inbox',
      description: 'View your emails',
      category: 'Navigation',
      action: () => router.push('/inbox'),
      keywords: ['email', 'mail'],
    },
    {
      id: 'calendar',
      label: 'Open Calendar',
      description: 'View your calendar',
      category: 'Navigation',
      action: () => router.push('/calendar'),
      keywords: ['events', 'schedule'],
    },
    {
      id: 'analytics',
      label: 'View Analytics',
      description: 'See your analytics',
      category: 'Navigation',
      action: () => router.push('/analytics'),
      keywords: ['stats', 'metrics'],
    },
    {
      id: 'visionhome',
      label: 'VisionHome AI',
      description: 'Scan properties',
      category: 'Features',
      action: () => router.push('/visionhome'),
      keywords: ['vision', 'scan', 'property'],
    },
    {
      id: 'neighborhood',
      label: 'Neighborhood Search',
      description: 'Search neighborhoods',
      category: 'Features',
      action: () => router.push('/neighborhood'),
      keywords: ['neighborhood', 'location'],
    },
    {
      id: 'settings',
      label: 'Settings',
      description: 'Open settings',
      category: 'Navigation',
      action: () => router.push('/settings'),
      keywords: ['preferences', 'config'],
    },
  ];

  return {
    isOpen,
    toggle,
    open,
    close,
    commands: defaultCommands,
  };
}

