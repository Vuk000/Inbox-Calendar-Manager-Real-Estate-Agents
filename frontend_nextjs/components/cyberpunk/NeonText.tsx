'use client';

import { ReactNode } from 'react';

interface NeonTextProps {
  children: ReactNode;
  color?: 'blue' | 'purple' | 'pink';
  className?: string;
}

export function NeonText({ 
  children, 
  color = 'blue',
  className = ''
}: NeonTextProps) {
  const colorClass = {
    blue: 'text-neon-blue',
    purple: 'text-neon-purple',
    pink: 'text-neon-pink',
  }[color];

  return (
    <span className={`${colorClass} ${className}`}>
      {children}
    </span>
  );
}

