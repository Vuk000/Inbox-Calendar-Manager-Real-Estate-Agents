import { ReactNode, HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  glow?: boolean;
  glass?: boolean;
}

export function Card({ className, children, glow = false, glass = false, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-xl border transition-premium',
        glass 
          ? 'glass-premium-light' 
          : 'bg-white dark:bg-dark-purple/50 border-gray-200 dark:border-neon-cyan/20',
        'p-6',
        'hover:shadow-premium-lg hover:scale-[1.02]',
        glow && 'shadow-glow',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

