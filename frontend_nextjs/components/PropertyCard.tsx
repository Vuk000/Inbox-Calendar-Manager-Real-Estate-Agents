'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import { Card } from './ui/card';
import { cn } from '@/lib/utils';

interface PropertyCardProps {
  id: number;
  title: string;
  image?: string;
  address?: string;
  price?: string;
  fitScore?: number;
  onClick?: () => void;
  className?: string;
}

export function PropertyCard({
  id,
  title,
  image,
  address,
  price,
  fitScore,
  onClick,
  className,
}: PropertyCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      whileHover={{ y: -5, scale: 1.02 }}
      transition={{ duration: 0.3 }}
      className={cn('cursor-pointer', className)}
      onClick={onClick}
    >
      <Card className="overflow-hidden h-full">
        {image && (
          <div className="relative w-full h-48 overflow-hidden">
            <Image
              src={image}
              alt={title}
              fill
              className="object-cover transition-transform duration-500 hover:scale-110"
            />
          </div>
        )}
        <div className="p-4">
          <h3 className="text-lg font-orbitron text-neon-cyan mb-2">{title}</h3>
          {address && <p className="text-sm text-gray-400 mb-2">{address}</p>}
          {price && <p className="text-xl font-bold text-neon-pink mb-2">{price}</p>}
          {fitScore !== undefined && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-400">Fit Score</span>
                <span className="text-sm font-bold text-neon-cyan">{fitScore}%</span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-2">
                <motion.div
                  className="h-2 bg-gradient-neon rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${fitScore}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                />
              </div>
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  );
}

