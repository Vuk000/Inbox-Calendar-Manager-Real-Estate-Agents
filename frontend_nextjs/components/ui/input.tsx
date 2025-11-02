'use client';

import { forwardRef, InputHTMLAttributes, TextareaHTMLAttributes, useState } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Eye, EyeOff, CheckCircle, XCircle } from 'lucide-react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  success?: boolean;
  mask?: 'phone' | 'date' | 'currency' | 'ssn';
}

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  success?: boolean;
}

// Input masks
const applyMask = (value: string, mask: string): string => {
  switch (mask) {
    case 'phone':
      return value.replace(/\D/g, '').replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    case 'date':
      return value.replace(/\D/g, '').replace(/(\d{2})(\d{2})(\d{4})/, '$1/$2/$3');
    case 'currency':
      return value.replace(/\D/g, '').replace(/(\d+)(\d{2})/, '$$$1.$2');
    case 'ssn':
      return value.replace(/\D/g, '').replace(/(\d{3})(\d{2})(\d{4})/, '$1-$2-$3');
    default:
      return value;
  }
};

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, success, mask, type = 'text', ...props }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const [focused, setFocused] = useState(false);
    const isPassword = type === 'password';

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (mask) {
        e.target.value = applyMask(e.target.value, mask);
      }
      props.onChange?.(e);
    };

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 dark:text-neon-cyan mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          <input
            ref={ref}
            type={isPassword && showPassword ? 'text' : type}
            className={cn(
              'w-full px-4 py-2 bg-white dark:bg-dark-purple/50 border rounded-lg',
              'text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500',
              'focus:outline-none focus:ring-2 focus:ring-offset-2',
              'transition-all duration-300',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              focused && !error && 'border-blue-500 dark:border-neon-cyan focus:ring-blue-500/50 dark:focus:ring-neon-cyan/50',
              error && 'border-red-500 focus:border-red-500 focus:ring-red-500/50',
              success && !error && 'border-green-500 focus:border-green-500 focus:ring-green-500/50',
              !focused && !error && !success && 'border-gray-300 dark:border-neon-cyan/30',
              isPassword && 'pr-10',
              className
            )}
            onFocus={(e) => {
              setFocused(true);
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              setFocused(false);
              props.onBlur?.(e);
            }}
            onChange={handleChange}
            aria-label={label}
            aria-invalid={!!error}
            aria-describedby={error ? `${props.id}-error` : undefined}
            {...props}
          />
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-neon-cyan transition-colors"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          )}
          {success && !error && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <CheckCircle className="w-5 h-5 text-green-500" />
            </motion.div>
          )}
          {error && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <XCircle className="w-5 h-5 text-red-500" />
            </motion.div>
          )}
        </div>
        {error && (
          <motion.p
            id={`${props.id}-error`}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-1 text-sm text-red-500"
            role="alert"
          >
            {error}
          </motion.p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, success, ...props }, ref) => {
    const [focused, setFocused] = useState(false);

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 dark:text-neon-cyan mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          <textarea
            ref={ref}
            className={cn(
              'w-full px-4 py-2 bg-white dark:bg-dark-purple/50 border rounded-lg',
              'text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500',
              'focus:outline-none focus:ring-2 focus:ring-offset-2',
              'transition-all duration-300 resize-y',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'min-h-[100px]',
              focused && !error && 'border-blue-500 dark:border-neon-cyan focus:ring-blue-500/50 dark:focus:ring-neon-cyan/50',
              error && 'border-red-500 focus:border-red-500 focus:ring-red-500/50',
              success && !error && 'border-green-500 focus:border-green-500 focus:ring-green-500/50',
              !focused && !error && !success && 'border-gray-300 dark:border-neon-cyan/30',
              className
            )}
            onFocus={(e) => {
              setFocused(true);
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              setFocused(false);
              props.onBlur?.(e);
            }}
            aria-label={label}
            aria-invalid={!!error}
            aria-describedby={error ? `${props.id}-error` : undefined}
            {...props}
          />
          {success && !error && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute right-3 top-3"
            >
              <CheckCircle className="w-5 h-5 text-green-500" />
            </motion.div>
          )}
          {error && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute right-3 top-3"
            >
              <XCircle className="w-5 h-5 text-red-500" />
            </motion.div>
          )}
        </div>
        {error && (
          <motion.p
            id={`${props.id}-error`}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-1 text-sm text-red-500"
            role="alert"
          >
            {error}
          </motion.p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
