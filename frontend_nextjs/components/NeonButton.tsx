'use client';

import { motion, HTMLMotionProps } from 'framer-motion';
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface NeonButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  children: ReactNode;
  pulse?: boolean;
}

export function NeonButton({ children, className, pulse = false, ...props }: NeonButtonProps) {
  const { onDrag, onDragStart, onDragEnd, ...motionProps } = props;
  
  return (
    <motion.button
      className={cn(
        'relative px-6 py-3 bg-gradient-neon text-dark-purple font-orbitron font-bold',
        'rounded-lg shadow-neon',
        'transition-all duration-300',
        className
      )}
      whileHover={{
        scale: 1.05,
        boxShadow: '0 0 20px rgba(0, 255, 255, 0.5)',
        transition: { duration: 0.2 },
      }}
      whileTap={{ scale: 0.95 }}
      animate={pulse ? {
        scale: [1, 1.05, 1],
        boxShadow: [
          '0 0 10px rgba(0, 255, 255, 0.5)',
          '0 0 30px rgba(0, 255, 255, 0.8)',
          '0 0 10px rgba(0, 255, 255, 0.5)',
        ],
        transition: {
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        },
      } : undefined}
      {...motionProps}
    >
      <span className="relative z-10">{children}</span>
    </motion.button>
  );
}

