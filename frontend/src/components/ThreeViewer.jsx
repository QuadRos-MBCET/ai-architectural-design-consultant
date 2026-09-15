import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Center, Environment, ContactShadows, useGLTF } from '@react-three/drei';

function Model({ url }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene} />;
}

export default function ThreeViewer({ modelUrl }) {
  if (!modelUrl) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
        <p style={{ color: '#666' }}>No 3D model generated yet.</p>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', minHeight: '600px', borderRadius: '8px', overflow: 'hidden', backgroundColor: '#e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      
      {/* UI Overlay Hint */}
      <div style={{ position: 'absolute', bottom: '15px', left: '0', right: '0', textAlign: 'center', zIndex: 20, pointerEvents: 'none' }}>
        <span style={{ backgroundColor: 'rgba(255,255,255,0.9)', padding: '8px 16px', borderRadius: '20px', fontSize: '14px', fontWeight: 'bold', color: '#374151', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          🖱️ Left Click & Drag to Rotate 360° | Scroll to Zoom
        </span>
      </div>

      <Canvas shadows camera={{ position: [25, 30, 35], fov: 40 }}>
        <color attach="background" args={['#0f1115']} />
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 20, 15]} intensity={1.5} castShadow />
        <Environment preset="city" />
        
        <Suspense fallback={null}>
          <Center>
            <Model url={modelUrl} />
            <ContactShadows position={[0, -0.1, 0]} opacity={0.8} scale={40} blur={2} far={4} color="#10b981" />
          </Center>
        </Suspense>
        
        {/* Architectural Grid */}
        <gridHelper args={[50, 50, '#334155', '#1e293b']} position={[0, -0.11, 0]} />
        
        <OrbitControls makeDefault autoRotate autoRotateSpeed={0.5} target={[0, 0, 0]} />
      </Canvas>
    </div>
  );
}
