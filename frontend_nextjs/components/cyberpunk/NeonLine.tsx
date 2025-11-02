'use client';

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';
import * as THREE from 'three';

interface NeonLineProps {
  from: [number, number, number];
  to: [number, number, number];
  color?: string;
  animated?: boolean;
  dashScale?: number;
}

export function NeonLine({ 
  from, 
  to, 
  color = '#00FFFF',
  animated = true,
  dashScale = 1
}: NeonLineProps) {
  const lineRef = useRef<THREE.Line2>(null);

  const points = useMemo(() => {
    return [from, to] as [THREE.Vector3, THREE.Vector3];
  }, [from, to]);

  useFrame((state) => {
    if (lineRef.current && animated) {
      lineRef.current.material.dashOffset -= 0.02 * dashScale;
    }
  });

  return (
    <Line
      ref={lineRef}
      points={points}
      color={color}
      lineWidth={2}
      dashed={animated}
      dashScale={dashScale}
      dashSize={0.5}
      gapSize={0.3}
    />
  );
}

