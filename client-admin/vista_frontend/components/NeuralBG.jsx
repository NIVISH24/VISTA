'use client';

import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { useMemo, useRef } from 'react';

function NeuralPoints() {
  const ref = useRef();

  const positions = useMemo(() => {
    const p = new Float32Array(3000 * 3);
    for (let i = 0; i < p.length; i++) {
      p[i] = (Math.random() - 0.5) * 12;
    }
    return p;
  }, []);

  useFrame(() => {
    if (ref.current) {
      ref.current.rotation.y += 0.0015;
      ref.current.rotation.x += 0.0008;
    }
  });

  return (
    <Points ref={ref} positions={positions} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#FF5E5B"
        size={0.025}
        sizeAttenuation
        depthWrite={false}
      />
    </Points>
  );
}

export default function NeuralBG() {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none">
      <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
        <NeuralPoints />
      </Canvas>
    </div>
  );
}
