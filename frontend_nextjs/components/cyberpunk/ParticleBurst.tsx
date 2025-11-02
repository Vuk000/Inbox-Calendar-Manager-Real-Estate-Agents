'use client';

import { useEffect, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

interface ParticleBurstProps {
  position: { x: number; y: number };
  color?: string;
  intensity?: number;
  particleCount?: number;
  onComplete?: () => void;
}

function ParticleBurstInner({ 
  position, 
  color = '#00FFFF', 
  intensity = 1,
  particleCount = 50,
  onComplete 
}: ParticleBurstProps) {
  const pointsRef = useRef<THREE.Points>(null);
  const [particles, setParticles] = useState<Float32Array | null>(null);
  const velocitiesRef = useRef<Float32Array>(new Float32Array(particleCount * 3));
  const lifeRef = useRef<number>(1);

  useEffect(() => {
    const positions = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount * 3);

    // Convert screen coordinates to normalized device coordinates (-1 to 1)
    const x = (position.x / window.innerWidth) * 2 - 1;
    const y = -(position.y / window.innerHeight) * 2 + 1;

    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      // Start at burst position in 3D space
      positions[i3] = x * 5; // Scale for 3D space
      positions[i3 + 1] = y * 5;
      positions[i3 + 2] = 0;

      // Random velocity (radial explosion)
      const angle = (Math.PI * 2 * i) / particleCount;
      const speed = (Math.random() * 0.1 + 0.05) * intensity;
      velocities[i3] = Math.cos(angle) * speed;
      velocities[i3 + 1] = Math.sin(angle) * speed;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.05;
    }

    velocitiesRef.current = velocities;
    setParticles(positions);
  }, [position, particleCount, intensity]);

  useFrame((state, delta) => {
    if (pointsRef.current && particles) {
      lifeRef.current -= delta * 2;

      const positions = pointsRef.current.geometry.attributes.position.array as Float32Array;
      const velocities = velocitiesRef.current;

      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        positions[i3] += velocities[i3];
        positions[i3 + 1] += velocities[i3 + 1];
        positions[i3 + 2] += velocities[i3 + 2];
        
        // Apply gravity
        velocities[i3 + 1] -= 0.01;
        
        // Fade out
        velocities[i3] *= 0.98;
        velocities[i3 + 1] *= 0.98;
        velocities[i3 + 2] *= 0.98;
      }

      pointsRef.current.geometry.attributes.position.needsUpdate = true;
      pointsRef.current.material.opacity = lifeRef.current;

      if (lifeRef.current <= 0 && onComplete) {
        onComplete();
      }
    }
  });

  if (!particles) return null;

  return (
    <Points ref={pointsRef} positions={particles} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color={color}
        size={0.05 * intensity}
        sizeAttenuation={true}
        depthWrite={false}
        opacity={lifeRef.current}
      />
    </Points>
  );
}

export function ParticleBurst(props: ParticleBurstProps) {
  return (
    <Canvas
      camera={{ position: [0, 0, 5], fov: 75 }}
      style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 9999 }}
    >
      <ambientLight intensity={0.5} />
      <ParticleBurstInner {...props} />
    </Canvas>
  );
}

