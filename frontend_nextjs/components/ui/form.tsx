'use client';

import { ReactNode, useState } from 'react';
import { useForm, UseFormReturn, FieldValues, Path } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { Input } from './input';
import { Button } from './button';
import { cn } from '@/lib/utils';

interface FormFieldProps<T extends FieldValues> {
  form: UseFormReturn<T>;
  name: Path<T>;
  label?: string;
  type?: string;
  placeholder?: string;
  mask?: 'phone' | 'date' | 'currency' | 'ssn';
  className?: string;
}

export function FormField<T extends FieldValues>({
  form,
  name,
  label,
  type = 'text',
  placeholder,
  mask,
  className,
}: FormFieldProps<T>) {
  const { register, formState } = form;
  const error = formState.errors[name]?.message as string | undefined;
  const value = form.watch(name);
  const success = value && !error;

  return (
    <Input
      {...register(name)}
      label={label}
      type={type}
      placeholder={placeholder}
      error={error}
      success={success}
      mask={mask}
      className={className}
    />
  );
}

interface FormProps<T extends FieldValues> {
  schema: z.ZodSchema<T>;
  onSubmit: (data: T) => void | Promise<void>;
  children: (form: UseFormReturn<T>) => ReactNode;
  className?: string;
  defaultValues?: Partial<T>;
}

export function Form<T extends FieldValues>({
  schema,
  onSubmit,
  children,
  className,
  defaultValues,
}: FormProps<T>) {
  const form = useForm<T>({
    resolver: zodResolver(schema),
    defaultValues: defaultValues as T,
    mode: 'onChange', // Real-time validation
  });

  const handleSubmit = async (data: T) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  return (
    <form onSubmit={form.handleSubmit(handleSubmit)} className={cn('space-y-4', className)}>
      {children(form)}
    </form>
  );
}

interface AutocompleteProps<T> {
  options: T[];
  value: string;
  onChange: (value: string) => void;
  onSelect: (option: T) => void;
  getOptionLabel: (option: T) => string;
  placeholder?: string;
  className?: string;
  maxHeight?: number;
}

export function Autocomplete<T>({
  options,
  value,
  onChange,
  onSelect,
  getOptionLabel,
  placeholder,
  className,
  maxHeight = 200,
}: AutocompleteProps<T>) {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);

  const filteredOptions = options.filter((option) =>
    getOptionLabel(option).toLowerCase().includes(value.toLowerCase())
  );

  const handleSelect = (option: T) => {
    onSelect(option);
    setIsOpen(false);
    setFocusedIndex(-1);
  };

  return (
    <div className={cn('relative', className)}>
      <Input
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setIsOpen(true);
        }}
        onFocus={() => setIsOpen(true)}
        placeholder={placeholder}
      />
      {isOpen && filteredOptions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="absolute z-50 w-full mt-2 bg-dark-purple border border-neon-cyan/50 rounded-lg shadow-neon-cyan overflow-hidden"
          style={{ maxHeight }}
        >
          <div className="overflow-y-auto" style={{ maxHeight }}>
            {filteredOptions.map((option, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleSelect(option)}
                onMouseEnter={() => setFocusedIndex(index)}
                className={cn(
                  'w-full px-4 py-2 text-left text-sm transition-colors',
                  'hover:bg-neon-cyan/10',
                  focusedIndex === index && 'bg-neon-cyan/20 text-neon-cyan',
                  'text-gray-300'
                )}
              >
                {getOptionLabel(option)}
              </button>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}

