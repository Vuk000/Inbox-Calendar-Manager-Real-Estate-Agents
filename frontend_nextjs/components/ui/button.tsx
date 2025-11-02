'use client';

import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'default' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  glow?: boolean;
  children: React.ReactNode;
}

export function Button({
  className,
  variant = 'primary',
  size = 'md',
  glow = false,
  children,
  ...props
}: ButtonProps) {
  return (
    <motion.button
      className={cn(
        'relative inline-flex items-center justify-center rounded-lg font-medium',
        'transition-premium',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        {
          'bg-gradient-neon text-dark-purple shadow-neon hover:shadow-neon-pink focus:ring-neon-cyan': variant === 'primary',
          'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 focus:ring-blue-500 shadow-premium hover:shadow-premium-lg': variant === 'default',
          'border-2 border-neon-cyan text-neon-cyan hover:bg-neon-cyan hover:text-dark-purple focus:ring-neon-cyan': variant === 'secondary',
          'border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 focus:ring-gray-500': variant === 'outline',
          'text-neon-cyan hover:bg-neon-cyan/10 focus:ring-neon-cyan': variant === 'ghost',
          'px-3 py-1.5 text-sm': size === 'sm',
          'px-4 py-2 text-base': size === 'md',
          'px-6 py-3 text-lg': size === 'lg',
        },
        glow && 'animate-pulse shadow-glow',
        className
      )}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
      {...props}
      role="button"
      tabIndex={props.disabled ? -1 : 0}
    >
      {children}
    </motion.button>
  );
}

