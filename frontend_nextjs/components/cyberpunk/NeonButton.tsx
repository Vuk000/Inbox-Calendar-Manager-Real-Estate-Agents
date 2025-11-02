'use client';

import { ReactNode, useState } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ParticleBurst } from './ParticleBurst';

interface NeonButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  children: ReactNode;
  glowColor?: 'blue' | 'purple' | 'pink';
  particleBurst?: boolean;
  variant?: 'primary' | 'secondary' | 'ghost' | 'default' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export function NeonButton({ 
  children, 
  glowColor = 'blue',
  particleBurst = true,
  onClick,
  className = '',
  variant = 'default',
  size = 'md',
  ...props 
}: NeonButtonProps) {
  const [burst, setBurst] = useState<{ x: number; y: number } | null>(null);

  const glowClass = {
    blue: 'shadow-neon-glow-blue border-neon-cyan',
    purple: 'shadow-neon-glow-purple border-neon-purple',
    pink: 'shadow-neon-glow-pink border-neon-pink',
  }[glowColor];

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (particleBurst) {
      const rect = e.currentTarget.getBoundingClientRect();
      setBurst({
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2,
      });
      setTimeout(() => setBurst(null), 1000);
    }
    onClick?.(e);
  };

  return (
    <>
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Button
          onClick={handleClick}
          variant={variant}
          size={size}
          className={`
            ${className}
            neon-border
            ${glowClass}
            animate-pulse-neon
            transition-all duration-300
          `}
          {...props}
        >
          {children}
        </Button>
      </motion.div>
      {burst && (
        <ParticleBurst
          position={burst}
          color={glowColor === 'blue' ? '#00FFFF' : glowColor === 'purple' ? '#A020F0' : '#FF00FF'}
          intensity={0.5}
          particleCount={30}
          onComplete={() => setBurst(null)}
        />
      )}
    </>
  );
}

