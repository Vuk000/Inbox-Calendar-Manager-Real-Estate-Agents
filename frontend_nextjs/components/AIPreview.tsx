'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import Image from 'next/image';
import { Card } from './ui/card';
import { ZoomIn, ZoomOut } from 'lucide-react';

interface AIPreviewProps {
  image: string;
  alt?: string;
  className?: string;
}

export function AIPreview({ image, alt = 'Preview', className }: AIPreviewProps) {
  const [isZoomed, setIsZoomed] = useState(false);

  return (
    <motion.div
      className={`relative ${className}`}
      whileHover={{ scale: 1.05 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="overflow-hidden p-2 border-2 border-neon-cyan/50">
        <div className="relative w-full h-64 overflow-hidden rounded-lg">
          <Image
            src={image}
            alt={alt}
            fill
            className={`object-cover transition-transform duration-500 ${
              isZoomed ? 'scale-150' : 'scale-100'
            }`}
            onClick={() => setIsZoomed(!isZoomed)}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-dark-purple/80 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300 flex items-end justify-center p-4">
            <button
              onClick={() => setIsZoomed(!isZoomed)}
              className="p-2 bg-neon-cyan/20 rounded-lg backdrop-blur-sm hover:bg-neon-cyan/40 transition-colors"
            >
              {isZoomed ? (
                <ZoomOut className="w-5 h-5 text-neon-cyan" />
              ) : (
                <ZoomIn className="w-5 h-5 text-neon-cyan" />
              )}
            </button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}

