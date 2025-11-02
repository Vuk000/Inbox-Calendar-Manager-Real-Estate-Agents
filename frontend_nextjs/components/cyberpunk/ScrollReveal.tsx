'use client';

import { ReactNode, useEffect, useRef } from 'react';
import { motion, useInView, useAnimation } from 'framer-motion';

interface ScrollRevealProps {
  children: ReactNode;
  delay?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
  className?: string;
}

export function ScrollReveal({ 
  children, 
  delay = 0,
  direction = 'up',
  className = ''
}: ScrollRevealProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const controls = useAnimation();

  useEffect(() => {
    if (isInView) {
      controls.start({
        opacity: 1,
        scale: 1,
        y: 0,
        x: 0,
        transition: { delay, duration: 0.6, ease: 'easeOut' },
      });
    }
  }, [isInView, controls, delay]);

  const initialVariants = {
    up: { opacity: 0, scale: 0.9, y: 50 },
    down: { opacity: 0, scale: 0.9, y: -50 },
    left: { opacity: 0, scale: 0.9, x: 50 },
    right: { opacity: 0, scale: 0.9, x: -50 },
  };

  return (
    <motion.div
      ref={ref}
      initial={initialVariants[direction]}
      animate={controls}
      className={className}
    >
      {children}
    </motion.div>
  );
}

