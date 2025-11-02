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
          : 'bg-dark-bg/50 border-neon-cyan/20 backdrop-blur-sm',
        'p-6',
        'hover:shadow-neon-glow-blue hover:scale-[1.02]',
        glow && 'shadow-neon-glow-blue',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

