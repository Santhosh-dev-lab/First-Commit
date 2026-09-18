"use client"

import { useState, useRef } from "react"
import { Canvas } from "@react-three/fiber"
import { OrbitControls, Environment } from "@react-three/drei"
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib'
import { useTwin } from "@/lib/api/client"
import { PolyhouseStructure } from "./PolyhouseStructure"
import { Zone3D } from "./Zone3D"
import { WaterSystem3D } from "./WaterSystem3D"

interface PolyhouseSceneProps {
  onSelectZone: (zoneId: string) => void
}

export function PolyhouseScene({ onSelectZone }: PolyhouseSceneProps) {
  const { data: twin } = useTwin()
  const [inspectionMode, setInspectionMode] = useState(false)
  const controlsRef = useRef<OrbitControlsImpl>(null)

  const handleCameraPreset = (preset: string) => {
    if (!controlsRef.current) return
    const controls = controlsRef.current
    
    switch(preset) {
      case 'overview':
        controls.object.position.set(20, 15, 25)
        controls.target.set(0, 0, 0)
        break
      case 'zone1':
        controls.object.position.set(-10, 5, -8)
        controls.target.set(0, 0, -4)
        break
      case 'zone2':
        controls.object.position.set(10, 5, 8)
        controls.target.set(0, 0, 4)
        break
      case 'infrastructure':
        controls.object.position.set(-15, 8, 5)
        controls.target.set(-10, 0, 0)
        break
    }
    controls.update()
  }

  return (
    <div className="w-full h-full relative">
      <div className="absolute top-4 right-4 z-10 flex gap-2">
        <button 
          onClick={() => setInspectionMode(!inspectionMode)}
          className={`px-3 py-1.5 text-[10px] font-mono tracking-widest uppercase rounded border transition-colors ${
            inspectionMode 
              ? 'bg-blue-500/20 text-blue-400 border-blue-500/50 shadow-[0_0_10px_rgba(59,130,246,0.2)]' 
              : 'bg-black/60 text-white/70 border-white/10 hover:bg-black/80'
          }`}
        >
          {inspectionMode ? 'Inspection Mode: ON' : 'Inspection Mode: OFF'}
        </button>
      </div>

      <div className="absolute bottom-4 left-4 z-10 flex gap-2">
        <span className="text-[10px] font-mono tracking-widest uppercase text-white/30 mr-2 flex items-center">Camera</span>
        {['overview', 'zone1', 'zone2', 'infrastructure'].map(preset => (
          <button 
            key={preset}
            onClick={() => handleCameraPreset(preset)}
            className="px-3 py-1.5 text-[10px] font-mono tracking-widest uppercase rounded border border-white/10 bg-black/60 text-white/70 hover:bg-black/80 hover:text-white transition-colors"
          >
            {preset}
          </button>
        ))}
      </div>

      <Canvas shadows camera={{ position: [20, 15, 25], fov: 45 }}>
        <color attach="background" args={['#101518']} />
        
        {/* Realistic Lighting & Environment */}
        <ambientLight intensity={0.6} />
        <directionalLight 
          position={[50, 40, -30]} 
          intensity={1.5} 
          castShadow 
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
          shadow-camera-far={100}
          shadow-camera-left={-20}
          shadow-camera-right={20}
          shadow-camera-top={20}
          shadow-camera-bottom={-20}
          shadow-bias={-0.0001}
        />
        
        <Environment preset="forest" background blur={0.8} />

        {/* Realistic Ground */}
        <mesh receiveShadow position={[0, -0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[100, 100]} />
          <meshStandardMaterial color="#2d332d" roughness={1} />
        </mesh>

        {/* Polyhouse Frame */}
        <PolyhouseStructure inspectionMode={inspectionMode} />

        {/* Dynamic Zones & Crops based on Twin State */}
        {twin?.zones.map((zone, idx) => (
          <Zone3D 
            key={zone.zone_id}
            zone={zone}
            index={idx}
            twin={twin}
            onSelect={() => onSelectZone(zone.zone_id)}
          />
        ))}

        {/* Water Infrastructure (Tank, Pipes, Pump) */}
        {twin && (
          <WaterSystem3D 
            tankVolume={twin.tank_volume_l}
            tankCapacity={twin.tank_capacity_l || 5000}
            pumpState={twin.pump_state}
          />
        )}

        <OrbitControls 
          ref={controlsRef}
          makeDefault
          minPolarAngle={Math.PI / 6}
          maxPolarAngle={Math.PI / 2.1}
          maxDistance={30}
        />
      </Canvas>
    </div>
  )
}
