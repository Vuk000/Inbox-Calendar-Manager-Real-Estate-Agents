'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

export function MagneticCursor() {
  const [isHovering, setIsHovering] = useState(false);
  const [isDesktop, setIsDesktop] = useState(false);
  const cursorRef = useRef<HTMLDivElement>(null);
  const cursorInnerRef = useRef<HTMLDivElement>(null);
  
  // Always initialize hooks - don't conditionally call them
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  
  const springConfig = { damping: 30, stiffness: 300 };
  const cursorX = useSpring(mouseX, springConfig);
  const cursorY = useSpring(mouseY, springConfig);
  
  const cursorInnerX = useSpring(cursorX, { damping: 20, stiffness: 400 });
  const cursorInnerY = useSpring(cursorY, { damping: 20, stiffness: 400 });

  // Transform values - always created
  const cursorXTransform = useTransform(cursorX, (value) => value - 16);
  const cursorYTransform = useTransform(cursorY, (value) => value - 16);
  const cursorInnerXTransform = useTransform(cursorInnerX, (value) => value - 4);
  const cursorInnerYTransform = useTransform(cursorInnerY, (value) => value - 4);
  const cursorGlowXTransform = useTransform(cursorX, (value) => value - 40);
  const cursorGlowYTransform = useTransform(cursorY, (value) => value - 40);

  useEffect(() => {
    // Only show on desktop with fine pointer
    const checkDesktop = () => {
      const desktop = typeof window !== 'undefined' && window.matchMedia('(pointer: fine)').matches;
      setIsDesktop(desktop);
      return desktop;
    };
    
    const desktop = checkDesktop();
    const handleResize = () => checkDesktop();
    if (typeof window !== 'undefined') {
      window.addEventListener('resize', handleResize);
    }

    const handleMouseMove = (e: MouseEvent) => {
      mouseX.set(e.clientX);
      mouseY.set(e.clientY);
    };

    // Detect interactive elements
    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName === 'BUTTON' ||
        target.tagName === 'A' ||
        target.closest('button') ||
        target.closest('a') ||
        target.closest('[data-magnetic]')
      ) {
        setIsHovering(true);
      }
    };

    const handleMouseOut = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName === 'BUTTON' ||
        target.tagName === 'A' ||
        target.closest('button') ||
        target.closest('a') ||
        target.closest('[data-magnetic]')
      ) {
        setIsHovering(false);
      }
    };

    if (desktop && typeof window !== 'undefined') {
      window.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseover', handleMouseOver);
      document.addEventListener('mouseout', handleMouseOut);
    }

    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('resize', handleResize);
        if (desktop) {
          window.removeEventListener('mousemove', handleMouseMove);
          document.removeEventListener('mouseover', handleMouseOver);
          document.removeEventListener('mouseout', handleMouseOut);
        }
      }
    };
  }, [mouseX, mouseY]);

  if (!isDesktop) return null;

  return (
    <>
      <motion.div
        ref={cursorRef}
        className="fixed top-0 left-0 w-8 h-8 rounded-full border-2 border-gray-400 pointer-events-none z-[9999] mix-blend-difference"
        style={{
          x: cursorXTransform,
          y: cursorYTransform,
          scale: isHovering ? 1.5 : 1,
        }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      />
      <motion.div
        ref={cursorInnerRef}
        className="fixed top-0 left-0 w-2 h-2 rounded-full bg-gray-900 pointer-events-none z-[9999] mix-blend-difference"
        style={{
          x: cursorInnerXTransform,
          y: cursorInnerYTransform,
        }}
      />
      <motion.div
        className="fixed top-0 left-0 w-20 h-20 rounded-full pointer-events-none z-[9998] mix-blend-difference"
        style={{
          x: cursorGlowXTransform,
          y: cursorGlowYTransform,
          background: 'radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%)',
          scale: isHovering ? 1.5 : 1,
        }}
        transition={{ type: 'spring', stiffness: 200, damping: 30 }}
      />
    </>
  );
}

