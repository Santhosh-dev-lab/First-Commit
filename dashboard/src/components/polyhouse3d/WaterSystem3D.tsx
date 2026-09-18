"use client"

import { useRef } from "react"
import * as THREE from "three"
import { useFrame } from "@react-three/fiber"
import { Html } from "@react-three/drei"

interface WaterSystemProps {
  tankVolume: number
  tankCapacity: number
  pumpState: string
}

export function WaterSystem3D({ tankVolume, tankCapacity, pumpState }: WaterSystemProps) {
  const waterFlowRef = useRef<THREE.Mesh>(null)
  
  useFrame((state, delta) => {
    if (pumpState === "ON" && waterFlowRef.current) {
      waterFlowRef.current.position.x = (state.clock.elapsedTime * 2) % 1
    }
  })

  // Position tank outside the main glass box, at x = -10, z = 0
  const tankRadius = 2
  const tankHeight = 4
  
  const fillRatio = Math.max(0, Math.min(1, tankVolume / tankCapacity))
  const fillHeight = tankHeight * fillRatio
  
  const isLow = fillRatio < 0.2

  return (
    <group position={[-10, 0, 0]}>
      {/* Concrete Pad */}
      <mesh position={[2, 0.1, 0]} receiveShadow>
        <boxGeometry args={[6, 0.2, 5]} />
        <meshStandardMaterial color="#666666" roughness={0.9} />
      </mesh>

      {/* Industrial Tank Shell */}
      <mesh position={[0, tankHeight/2 + 0.2, 0]} castShadow>
        <cylinderGeometry args={[tankRadius, tankRadius, tankHeight, 32]} />
        <meshPhysicalMaterial 
          color="#1e3a8a" // Dark industrial blue
          roughness={0.6}
          metalness={0.2}
          clearcoat={0.1}
        />
      </mesh>
      
      {/* Tank Ribs for structural realism */}
      {[0.5, 1.5, 2.5, 3.5].map(y => (
        <mesh key={y} position={[0, y + 0.2, 0]} castShadow>
          <torusGeometry args={[tankRadius, 0.05, 8, 32]} />
          <meshStandardMaterial color="#1e3a8a" roughness={0.7} />
        </mesh>
      ))}

      {/* Tank Lid */}
      <mesh position={[0, tankHeight + 0.25, 0]} castShadow>
        <cylinderGeometry args={[tankRadius + 0.05, tankRadius + 0.05, 0.1, 32]} />
        <meshStandardMaterial color="#111827" roughness={0.8} />
      </mesh>

      {/* Water Fill Level (Visible if we added a cutaway or sight glass, but let's just make it physical inside for now, or assume the UI tells us) */}

      {/* HTML Overlay Label for Tank */}
      <Html position={[0, tankHeight + 2, 0]} center zIndexRange={[100, 0]}>
        <div className="flex flex-col gap-1 px-3 py-2 rounded-lg border border-white/10 bg-black/60 backdrop-blur-md shadow-2xl">
          <span className="text-white text-xs font-mono">Water Tank</span>
          <div className="flex items-center gap-2">
            <span className="text-blue-400 font-bold text-lg">{Math.round(tankVolume).toLocaleString()} L</span>
            <span className="text-white/40 text-sm">/ {tankCapacity.toLocaleString()} L</span>
          </div>
          <div className="w-full h-1 bg-white/10 rounded-full mt-1 overflow-hidden">
            <div className={`h-full ${isLow ? 'bg-red-500' : 'bg-blue-500'}`} style={{ width: `${fillRatio * 100}%` }} />
          </div>
        </div>
      </Html>

      {/* Detailed Pump Motor */}
      <group position={[tankRadius + 1, 0.5, 0]}>
        {/* Pump Base */}
        <mesh position={[0, -0.15, 0]} castShadow>
          <boxGeometry args={[0.8, 0.1, 0.5]} />
          <meshStandardMaterial color="#333" metalness={0.8} roughness={0.4} />
        </mesh>
        
        {/* Pump Motor Cylinder */}
        <mesh position={[0, 0.1, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
          <cylinderGeometry args={[0.25, 0.25, 0.6, 16]} />
          <meshStandardMaterial color={pumpState === "ON" ? "#10b981" : "#52525b"} metalness={0.6} roughness={0.3} />
        </mesh>
        
        {/* Pump Impeller Housing */}
        <mesh position={[0.4, 0.1, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
          <cylinderGeometry args={[0.3, 0.3, 0.2, 16]} />
          <meshStandardMaterial color="#111" metalness={0.9} roughness={0.2} />
        </mesh>
        
        {/* HTML Overlay Label for Pump */}
        <Html position={[0, 1.5, 0]} center zIndexRange={[100, 0]}>
          <div className="flex flex-col gap-1 px-3 py-2 rounded-lg border border-white/10 bg-black/60 backdrop-blur-md shadow-2xl">
            <span className="text-white text-xs font-mono">Pump P-01</span>
            <div className="flex items-center gap-2 mt-1">
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${pumpState === "ON" ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/50" : "bg-white/5 text-white/50 border border-white/10"}`}>
                {pumpState}
              </span>
            </div>
          </div>
        </Html>
      </group>

      {/* Pipes */}
      <group>
        {/* Tank to Pump Pipe */}
        <mesh position={[tankRadius + 0.5, 0.6, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
          <cylinderGeometry args={[0.08, 0.08, 1, 16]} />
          <meshStandardMaterial color="#1f2937" roughness={0.2} />
        </mesh>
        
        {/* Main Irrigation Pipe from Pump to Polyhouse */}
        <mesh position={[tankRadius + 2.5, 0.6, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
          <cylinderGeometry args={[0.08, 0.08, 2.2, 16]} />
          <meshStandardMaterial color="#1f2937" roughness={0.2} />
        </mesh>
        
        {/* Water flow indicator */}
        {pumpState === "ON" && (
          <group position={[tankRadius + 2.5, 0.6, 0]} rotation={[0, 0, Math.PI / 2]}>
            <mesh ref={waterFlowRef}>
              <cylinderGeometry args={[0.085, 0.085, 0.5, 8]} />
              <meshBasicMaterial color="#3b82f6" transparent opacity={0.6} />
            </mesh>
          </group>
        )}
      </group>
    </group>
  )
}
