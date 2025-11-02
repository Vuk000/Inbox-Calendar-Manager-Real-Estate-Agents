'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface CheckboxProps {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  disabled?: boolean;
  className?: string;
  children?: ReactNode;
}

export function Checkbox({ checked, onCheckedChange, disabled, className, children }: CheckboxProps) {
  return (
    <label className={cn('flex items-center gap-2 cursor-pointer', disabled && 'opacity-50 cursor-not-allowed', className)}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onCheckedChange?.(e.target.checked)}
        disabled={disabled}
        className="w-4 h-4 text-neon-cyan bg-dark-purple border-neon-cyan/30 rounded focus:ring-neon-cyan focus:ring-2"
      />
      {children}
    </label>
  );
}

