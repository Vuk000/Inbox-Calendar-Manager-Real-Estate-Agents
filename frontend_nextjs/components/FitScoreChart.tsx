'use client';

import { motion } from 'framer-motion';
import { Card } from './ui/card';
import { cn } from '@/lib/utils';

interface FitScoreChartProps {
  score: number;
  label?: string;
  size?: number;
  className?: string;
}

export function FitScoreChart({ score, label, size = 120, className }: FitScoreChartProps) {
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getColor = (score: number) => {
    if (score >= 80) return '#00FFFF'; // neon-cyan
    if (score >= 60) return '#A855F7'; // neon-purple
    return '#FF00FF'; // neon-pink
  };

  return (
    <Card className={cn('flex flex-col items-center p-6', className)}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgba(0, 255, 255, 0.1)"
            strokeWidth="8"
            fill="none"
          />
          {/* Progress circle */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={getColor(score)}
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            style={{
              filter: `drop-shadow(0 0 10px ${getColor(score)})`,
            }}
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-3xl font-orbitron font-bold"
            style={{ color: getColor(score) }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: 'spring' }}
          >
            {score}%
          </motion.span>
          {label && (
            <span className="text-xs text-gray-400 mt-1">{label}</span>
          )}
        </div>
      </div>
      
      {/* Particle effect on high scores */}
      {score >= 80 && (
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-neon-cyan rounded-full"
              style={{
                left: `${50 + (Math.random() - 0.5) * 20}%`,
                top: `${50 + (Math.random() - 0.5) * 20}%`,
              }}
              animate={{
                y: [0, -30, -60],
                opacity: [1, 0.5, 0],
                scale: [1, 1.5, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.2,
              }}
            />
          ))}
        </div>
      )}
    </Card>
  );
}

