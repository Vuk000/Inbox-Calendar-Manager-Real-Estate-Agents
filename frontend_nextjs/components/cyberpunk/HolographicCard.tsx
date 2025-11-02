'use client';

import { ReactNode, useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { HTMLAttributes } from 'react';

interface HolographicCardProps extends Omit<HTMLAttributes<HTMLDivElement>, 'children'> {
  children: ReactNode;
  glowColor?: 'blue' | 'purple' | 'pink';
}

export function HolographicCard({ 
  children, 
  glowColor = 'blue',
  className = '',
  ...props 
}: HolographicCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const glowClass = {
    blue: 'shadow-neon-glow-blue',
    purple: 'shadow-neon-glow-purple',
    pink: 'shadow-neon-glow-pink',
  }[glowColor];

  return (
    <motion.div
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      whileHover={{ 
        scale: 1.02,
        rotateY: 5,
        rotateX: -5,
      }}
      transition={{ duration: 0.3 }}
      style={{ transformStyle: 'preserve-3d', perspective: '1000px' }}
    >
      <Card
        className={`
          ${className}
          holographic-effect
          neon-border
          ${isHovered ? glowClass : ''}
          transition-all duration-300
          bg-dark-bg/50
          backdrop-blur-sm
        `}
        {...props}
      >
        {children}
      </Card>
    </motion.div>
  );
}

