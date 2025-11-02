'use client';

import { ReactNode, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  position?: 'left' | 'right' | 'top' | 'bottom';
  title?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const positionStyles = {
  left: 'left-0 top-0 h-full',
  right: 'right-0 top-0 h-full',
  top: 'top-0 left-0 w-full',
  bottom: 'bottom-0 left-0 w-full',
};

const sizeStyles = {
  sm: 'w-80',
  md: 'w-96',
  lg: 'w-[32rem]',
};

const slideVariants = {
  left: {
    hidden: { x: '-100%' },
    visible: { x: 0 },
  },
  right: {
    hidden: { x: '100%' },
    visible: { x: 0 },
  },
  top: {
    hidden: { y: '-100%' },
    visible: { y: 0 },
  },
  bottom: {
    hidden: { y: '100%' },
    visible: { y: 0 },
  },
};

export function Drawer({
  isOpen,
  onClose,
  children,
  position = 'right',
  title,
  size = 'md',
  className,
}: DrawerProps) {
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
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-dark-purple/80 backdrop-blur-sm z-50"
            onClick={onClose}
            aria-hidden="true"
          />
          <motion.div
            variants={slideVariants[position]}
            initial="hidden"
            animate="visible"
            exit="hidden"
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className={cn(
              'fixed z-50 bg-dark-purple border border-neon-cyan/50 shadow-neon-cyan',
              position === 'left' || position === 'right' 
                ? `${sizeStyles[size]} max-w-[90vw] h-full` 
                : 'h-96 max-h-[90vh] w-full',
              positionStyles[position],
              className
            )}
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? 'drawer-title' : undefined}
          >
            {title && (
              <div className="flex items-center justify-between p-4 border-b border-neon-cyan/20">
                <h2 id="drawer-title" className="text-xl font-orbitron font-bold text-neon-cyan">
                  {title}
                </h2>
                <button
                  onClick={onClose}
                  className="p-1 hover:bg-neon-cyan/20 rounded transition-colors"
                  aria-label="Close drawer"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
            )}
            <div className="overflow-y-auto h-full">{children}</div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  title?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const dialogSizeStyles = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
};

export function Dialog({
  isOpen,
  onClose,
  children,
  title,
  description,
  size = 'md',
  className,
}: DialogProps) {
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
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-dark-purple/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={onClose}
            aria-hidden="true"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.3 }}
            className={cn(
              'relative z-50 w-full bg-dark-purple border border-neon-cyan/50 rounded-xl shadow-neon-cyan',
              dialogSizeStyles[size],
              className
            )}
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? 'dialog-title' : undefined}
            aria-describedby={description ? 'dialog-description' : undefined}
            onClick={(e) => e.stopPropagation()}
          >
            {(title || onClose) && (
              <div className="flex items-center justify-between p-6 border-b border-neon-cyan/20">
                <div>
                  {title && (
                    <h2 id="dialog-title" className="text-2xl font-orbitron font-bold text-neon-cyan">
                      {title}
                    </h2>
                  )}
                  {description && (
                    <p id="dialog-description" className="mt-1 text-sm text-gray-400">
                      {description}
                    </p>
                  )}
                </div>
                <button
                  onClick={onClose}
                  className="p-1 hover:bg-neon-cyan/20 rounded transition-colors"
                  aria-label="Close dialog"
                >
                  <X className="w-5 h-5 text-gray-400" />
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

interface ConfirmationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
}

export function ConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'info',
}: ConfirmationDialogProps) {
  const variantStyles = {
    danger: 'bg-red-500/20 text-red-400 border-red-500/50 hover:bg-red-500/30',
    warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50 hover:bg-yellow-500/30',
    info: 'bg-neon-cyan/20 text-neon-cyan border-neon-cyan/50 hover:bg-neon-cyan/30',
  };

  return (
    <Dialog isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <p className="text-gray-300 mb-6">{message}</p>
      <div className="flex gap-4 justify-end">
        <button
          onClick={onClose}
          className="px-4 py-2 border border-neon-cyan/30 rounded-lg hover:bg-neon-cyan/10 transition-colors"
        >
          {cancelText}
        </button>
        <button
          onClick={() => {
            onConfirm();
            onClose();
          }}
          className={cn('px-4 py-2 border rounded-lg transition-colors', variantStyles[variant])}
        >
          {confirmText}
        </button>
      </div>
    </Dialog>
  );
}

