'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'neon';
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
  className?: string;
}

const variantStyles = {
  default: 'bg-gray-700 text-gray-300 border-gray-600',
  success: 'bg-green-500/20 text-green-400 border-green-500/50',
  warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
  error: 'bg-red-500/20 text-red-400 border-red-500/50',
  info: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
  neon: 'bg-neon-cyan/20 text-neon-cyan border-neon-cyan/50 shadow-neon-cyan',
};

const sizeStyles = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-sm',
  lg: 'px-4 py-1.5 text-base',
};

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  animated = false,
  className,
}: BadgeProps) {
  const baseStyles = 'inline-flex items-center justify-center rounded-full font-medium border transition-all duration-300';

  const badge = (
    <span
      className={cn(
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        animated && 'animate-pulse',
        className
      )}
    >
      {children}
    </span>
  );

  if (animated) {
    return (
      <motion.span
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
      >
        {badge}
      </motion.span>
    );
  }

  return badge;
}

// Count Badge variant
interface CountBadgeProps {
  count: number;
  max?: number;
  variant?: BadgeProps['variant'];
  showZero?: boolean;
}

export function CountBadge({ count, max, variant = 'neon', showZero = false }: CountBadgeProps) {
  if (!showZero && count === 0) return null;

  const displayCount = max && count > max ? `${max}+` : count.toString();

  return (
    <Badge variant={variant} size="sm" animated={count > 0}>
      {displayCount}
    </Badge>
  );
}

