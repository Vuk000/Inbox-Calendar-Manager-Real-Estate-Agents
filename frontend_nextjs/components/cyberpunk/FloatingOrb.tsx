'use client';

import { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Float, Sphere } from '@react-three/drei';
import * as THREE from 'three';

interface FloatingOrbProps {
  color?: string;
  size?: number;
  position?: [number, number, number];
  onClick?: () => void;
  speed?: number;
}

export function FloatingOrb({ 
  color = '#00FFFF', 
  size = 1, 
  position = [0, 0, 0],
  onClick,
  speed = 1
}: FloatingOrbProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += 0.01 * speed;
      meshRef.current.rotation.y += 0.01 * speed;
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * speed) * 0.2;
    }
  });

  return (
    <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>
      <Sphere
        ref={meshRef}
        args={[size, 32, 32]}
        position={position}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={hovered ? 2 : 1}
          metalness={0.8}
          roughness={0.2}
        />
      </Sphere>
    </Float>
  );
}

