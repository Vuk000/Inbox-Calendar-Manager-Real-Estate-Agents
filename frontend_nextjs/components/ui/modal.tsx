'use client';

import { ReactNode, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export function Modal({ isOpen, onClose, title, children, size = 'md' }: ModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className={cn(
              'fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50',
              'bg-dark-purple border border-neon-cyan rounded-xl shadow-neon',
              'max-h-[90vh] overflow-y-auto',
              {
                'w-full max-w-sm': size === 'sm',
                'w-full max-w-md': size === 'md',
                'w-full max-w-lg': size === 'lg',
                'w-full max-w-2xl': size === 'xl',
              }
            )}
          >
            {title && (
              <div className="flex items-center justify-between p-6 border-b border-neon-cyan/20">
                <h2 className="text-xl font-orbitron text-neon-cyan">{title}</h2>
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-neon-cyan transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
            )}
            <div className="p-6">{children}</div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

