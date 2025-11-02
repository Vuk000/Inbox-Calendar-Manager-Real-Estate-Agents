'use client';

import { motion } from 'framer-motion';
import { Modal } from './ui/modal';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Sparkles } from 'lucide-react';

interface UpsellModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  message: string;
  ctaText?: string;
  onCtaClick?: () => void;
  feature?: string;
}

export function UpsellModal({
  isOpen,
  onClose,
  title,
  message,
  ctaText = 'Upgrade Now',
  onCtaClick,
  feature,
}: UpsellModalProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="md">
      <div className="space-y-6">
        {/* Starfield background effect */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
          {[...Array(50)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-white rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                opacity: [0.3, 1, 0.3],
                scale: [1, 1.5, 1],
              }}
              transition={{
                duration: 2 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>
        
        <div className="relative z-10">
          {feature && (
            <Card className="mb-4 bg-gradient-neon/10 border-neon-cyan/50">
              <div className="flex items-center gap-2 text-neon-cyan">
                <Sparkles className="w-5 h-5" />
                <span className="font-orbitron">{feature}</span>
              </div>
            </Card>
          )}
          
          <p className="text-gray-300 mb-6">{message}</p>
          
          <div className="flex gap-4">
            <Button onClick={onClose} variant="ghost">
              Maybe Later
            </Button>
            <Button onClick={onCtaClick || onClose} variant="primary" glow>
              {ctaText}
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}

