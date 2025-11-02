'use client';

import { useCallback, useState, DragEvent } from 'react';
import { motion } from 'framer-motion';
import { Upload, X, File } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from './button';

interface FileUploadProps {
  onUpload: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
  maxSize?: number; // in MB
  className?: string;
  label?: string;
}

export function FileUpload({
  onUpload,
  accept,
  multiple = false,
  maxSize = 10,
  className,
  label = 'Upload files',
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [errors, setErrors] = useState<string[]>([]);

  const validateFile = (file: File): string | null => {
    if (maxSize && file.size > maxSize * 1024 * 1024) {
      return `File ${file.name} exceeds maximum size of ${maxSize}MB`;
    }
    if (accept && !accept.split(',').some((type) => file.type.match(type.trim()))) {
      return `File ${file.name} is not an accepted file type`;
    }
    return null;
  };

  const handleFiles = useCallback(
    (fileList: FileList | null) => {
      if (!fileList) return;

      const newFiles = Array.from(fileList);
      const validFiles: File[] = [];
      const newErrors: string[] = [];

      newFiles.forEach((file) => {
        const error = validateFile(file);
        if (error) {
          newErrors.push(error);
        } else {
          validFiles.push(file);
        }
      });

      if (validFiles.length > 0) {
        const updatedFiles = multiple ? [...files, ...validFiles] : validFiles;
        setFiles(updatedFiles);
        onUpload(updatedFiles);
      }

      if (newErrors.length > 0) {
        setErrors(newErrors);
        setTimeout(() => setErrors([]), 5000);
      }
    },
    [files, multiple, maxSize, accept, onUpload]
  );

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  const removeFile = (index: number) => {
    const updatedFiles = files.filter((_, i) => i !== index);
    setFiles(updatedFiles);
    onUpload(updatedFiles);
  };

  return (
    <div className={cn('w-full', className)}>
      {label && (
        <label className="block text-sm font-medium text-neon-cyan mb-2">
          {label}
        </label>
      )}
      <motion.div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        animate={{
          borderColor: isDragging ? '#00FFFF' : 'rgba(0, 255, 255, 0.3)',
          backgroundColor: isDragging ? 'rgba(0, 255, 255, 0.1)' : 'transparent',
        }}
        className={cn(
          'relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300',
          'hover:border-neon-cyan hover:bg-neon-cyan/5'
        )}
      >
        <input
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleInputChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          aria-label={label}
        />
        <Upload className="w-12 h-12 text-neon-cyan mx-auto mb-4" />
        <p className="text-gray-300 mb-2">
          {isDragging ? 'Drop files here' : 'Drag & drop files here or click to browse'}
        </p>
        <p className="text-sm text-gray-500">
          Max size: {maxSize}MB {accept && `• Accepted: ${accept}`}
        </p>
      </motion.div>

      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((file, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="flex items-center justify-between p-3 bg-dark-purple/50 rounded-lg border border-neon-cyan/20"
            >
              <div className="flex items-center gap-3">
                <File className="w-5 h-5 text-neon-cyan" />
                <div>
                  <p className="text-sm text-white">{file.name}</p>
                  <p className="text-xs text-gray-400">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="p-1 hover:bg-red-500/20 rounded transition-colors"
                aria-label={`Remove ${file.name}`}
              >
                <X className="w-4 h-4 text-red-400" />
              </button>
            </motion.div>
          ))}
        </div>
      )}

      {errors.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 space-y-1"
        >
          {errors.map((error, index) => (
            <p key={index} className="text-sm text-red-500">
              {error}
            </p>
          ))}
        </motion.div>
      )}
    </div>
  );
}

