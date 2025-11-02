'use client';

import { useRef, useMemo, useEffect, Suspense, useState, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Points, PointMaterial, Float } from '@react-three/drei';
import * as THREE from 'three';
import { motion } from 'framer-motion';

interface ParticleSystemProps {
  mouse: [number, number];
  count?: number;
  color?: string;
  speed?: number;
}

function ParticleSystem({ mouse, count = 2000, color = '#00FFFF', speed = 1 }: ParticleSystemProps) {
  const pointsRef = useRef<THREE.Points>(null);
  const lastUpdateTime = useRef(0);
  const throttleDelay = 16; // ~60fps

  const particles = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 20;
      
      // Random velocities
      velocities[i * 3] = (Math.random() - 0.5) * 0.02;
      velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.02;
      velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.02;
    }
    return { positions, velocities };
  }, [count]);

  useFrame((state, delta) => {
    const now = performance.now();
    if (now - lastUpdateTime.current < throttleDelay) return;
    lastUpdateTime.current = now;

    if (pointsRef.current) {
      pointsRef.current.rotation.x += delta * 0.05 * speed;
      pointsRef.current.rotation.y += delta * 0.03 * speed;
      
      // Enhanced mouse interaction with smoother response
      const positions = pointsRef.current.geometry.attributes.position.array as Float32Array;
      const velocities = particles.velocities;
      
      for (let i = 0; i < count; i++) {
        const i3 = i * 3;
        const x = positions[i3];
        const y = positions[i3 + 1];
        
        // Mouse attraction/repulsion
        const dx = x - mouse[0] * 5;
        const dy = y - mouse[1] * 5;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 4) {
          const force = (4 - distance) / 4;
          const attract = distance < 2 ? 1 : -0.5; // Attract when close, repel when further
          velocities[i3] += (dx * force * attract * delta * 3) * speed;
          velocities[i3 + 1] += (dy * force * attract * delta * 3) * speed;
        }
        
        // Apply velocities with damping
        positions[i3] += velocities[i3] * speed;
        positions[i3 + 1] += velocities[i3 + 1] * speed;
        positions[i3 + 2] += velocities[i3 + 2] * speed;
        
        // Damping
        velocities[i3] *= 0.98;
        velocities[i3 + 1] *= 0.98;
        velocities[i3 + 2] *= 0.98;
        
        // Boundary wrapping
        if (Math.abs(positions[i3]) > 10) velocities[i3] *= -0.5;
        if (Math.abs(positions[i3 + 1]) > 10) velocities[i3 + 1] *= -0.5;
        if (Math.abs(positions[i3 + 2]) > 10) velocities[i3 + 2] *= -0.5;
      }
      
      pointsRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <Points ref={pointsRef} positions={particles.positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color={color}
        size={0.05}
        sizeAttenuation={true}
        depthWrite={false}
        opacity={0.8}
      />
    </Points>
  );
}

function MouseTrail() {
  const trailRef = useRef<THREE.Points>(null);
  const trailLength = 50;
  const trailPositions = useRef<Float32Array>(new Float32Array(trailLength * 3));
  const trailIndex = useRef(0);

  useFrame((state, delta) => {
    if (trailRef.current) {
      // Update trail positions
      const index = trailIndex.current * 3;
      trailPositions.current[index] = (state.mouse.x * 5);
      trailPositions.current[index + 1] = (state.mouse.y * 5);
      trailPositions.current[index + 2] = -2;
      
      trailIndex.current = (trailIndex.current + 1) % trailLength;
      trailRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <Points ref={trailRef} positions={trailPositions.current} stride={3}>
      <PointMaterial
        transparent
        color="#FF00FF"
        size={0.1}
        sizeAttenuation={true}
        depthWrite={false}
        opacity={0.5}
      />
    </Points>
  );
}

function NebulaCloud() {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.z += delta * 0.05;
      meshRef.current.position.x = Math.sin(state.clock.elapsedTime * 0.1) * 2;
      meshRef.current.position.y = Math.cos(state.clock.elapsedTime * 0.15) * 2;
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, -8]}>
      <planeGeometry args={[15, 15]} />
      <meshBasicMaterial
        color="#FF00FF"
        transparent
        opacity={0.15}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

function ScrollReactivePlane() {
  const meshRef = useRef<THREE.Mesh>(null);
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useFrame((state, delta) => {
    if (meshRef.current && meshRef.current.material instanceof THREE.Material) {
      meshRef.current.rotation.z += delta * 0.1;
      meshRef.current.material.opacity = 0.2 + Math.sin(state.clock.elapsedTime + scrollY * 0.001) * 0.1;
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, -5]} rotation={[0, 0, 0]}>
      <planeGeometry args={[20, 20]} />
      <meshBasicMaterial
        color="#00FFFF"
        transparent
        opacity={0.2}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

function EnhancedGradientPlane() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state, delta) => {
    if (meshRef.current && meshRef.current.material instanceof THREE.Material) {
      meshRef.current.rotation.z += delta * 0.08;
      meshRef.current.material.opacity = 0.2 + Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, -5]} rotation={[0, 0, 0]}>
      <planeGeometry args={[20, 20]} />
      <meshBasicMaterial
        color="#FF00FF"
        transparent
        opacity={0.2}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

function NeonLineGrid() {
  const linesRef = useRef<THREE.Group>(null);
  const lineCount = 10;
  const lineLength = 10;

  const linePoints = useMemo(() => {
    const points: THREE.Vector3[][] = [];
    for (let i = 0; i < lineCount; i++) {
      const x = (i / lineCount - 0.5) * 20;
      points.push([
        new THREE.Vector3(x, -lineLength / 2, -3),
        new THREE.Vector3(x, lineLength / 2, -3),
      ]);
      points.push([
        new THREE.Vector3(-lineLength / 2, x, -3),
        new THREE.Vector3(lineLength / 2, x, -3),
      ]);
    }
    return points;
  }, []);

  useFrame((state) => {
    if (linesRef.current) {
      linesRef.current.rotation.z += 0.001;
    }
  });

  return (
    <group ref={linesRef}>
      {linePoints.map((points, i) => (
        <line key={i} points={points}>
          <lineBasicMaterial color="#00FFFF" transparent opacity={0.3} />
        </line>
      ))}
    </group>
  );
}

function FloatingOrbs() {
  const orbPositions = useMemo(() => [
    [5, 3, -2],
    [-5, -3, -2],
    [0, 5, -3],
    [-3, 0, -2],
  ] as [number, number, number][], []);

  return (
    <>
      {orbPositions.map((pos, i) => (
        <Float key={i} speed={1.5 + i * 0.5} rotationIntensity={0.5} floatIntensity={0.5}>
          <mesh position={pos}>
            <sphereGeometry args={[0.3, 16, 16]} />
            <meshStandardMaterial
              color={i % 2 === 0 ? '#00FFFF' : '#FF00FF'}
              emissive={i % 2 === 0 ? '#00FFFF' : '#FF00FF'}
              emissiveIntensity={1}
              metalness={0.8}
              roughness={0.2}
            />
          </mesh>
        </Float>
      ))}
    </>
  );
}

export default function WebGLBackground() {
  const mouseRef = useRef<[number, number]>([0, 0]);
  const throttledMouseRef = useRef<[number, number]>([0, 0]);
  const lastMouseUpdate = useRef(0);

  const updateMousePosition = useCallback((e: MouseEvent) => {
    const now = performance.now();
    if (now - lastMouseUpdate.current < 16) return; // Throttle to ~60fps
    lastMouseUpdate.current = now;
    
    mouseRef.current = [
      (e.clientX / window.innerWidth) * 2 - 1,
      -(e.clientY / window.innerHeight) * 2 + 1,
    ];
    
    // Smooth interpolation
    throttledMouseRef.current[0] += (mouseRef.current[0] - throttledMouseRef.current[0]) * 0.1;
    throttledMouseRef.current[1] += (mouseRef.current[1] - throttledMouseRef.current[1]) * 0.1;
  }, []);

  useEffect(() => {
    window.addEventListener('mousemove', updateMousePosition, { passive: true });
    return () => window.removeEventListener('mousemove', updateMousePosition);
  }, [updateMousePosition]);

  return (
    <motion.div
      className="fixed inset-0 -z-10"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
      <Suspense fallback={<div className="absolute inset-0 bg-dark-bg" />}>
        <Canvas
          camera={{ position: [0, 0, 5], fov: 75 }}
          gl={{ 
            alpha: true, 
            antialias: true, 
            powerPreference: 'high-performance',
            stencil: false,
            depth: true,
          }}
          style={{ background: 'transparent' }}
          dpr={[1, Math.min(window.devicePixelRatio, 2)]} // Limit pixel ratio for performance
          performance={{ min: 0.5 }} // Adaptive quality
        >
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} color="#00FFFF" intensity={1} />
          <pointLight position={[-10, -10, -10]} color="#FF00FF" intensity={1} />
          
          {/* Multiple particle systems - adaptive count based on device */}
          <ParticleSystem 
            mouse={throttledMouseRef.current} 
            count={typeof window !== 'undefined' && window.innerWidth < 768 ? 500 : 2000} 
            color="#00FFFF" 
            speed={1} 
          />
          <ParticleSystem 
            mouse={throttledMouseRef.current} 
            count={typeof window !== 'undefined' && window.innerWidth < 768 ? 300 : 1500} 
            color="#FF00FF" 
            speed={0.7} 
          />
          
          {/* Mouse trail */}
          <MouseTrail />
          
          {/* Nebula cloud */}
          <NebulaCloud />
          
          {/* Scroll-reactive plane */}
          <ScrollReactivePlane />
          
          {/* Enhanced gradient plane */}
          <EnhancedGradientPlane />
          
          {/* Neon line grid */}
          <NeonLineGrid />
          
          {/* Floating orbs */}
          <FloatingOrbs />
        </Canvas>
      </Suspense>
    </motion.div>
  );
}
