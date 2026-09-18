"use client"

import { useState } from "react"
import { Html } from "@react-three/drei"

interface SensorProps {
  position: [number, number, number]
  health: string
  twin?: any
}

export function Sensor3D({ position, health, twin }: SensorProps) {
  const [hovered, setHovered] = useState(false)
  const isHealthy = health === "HEALTHY"
  
  return (
    <group 
      position={position}
      onPointerEnter={(e) => { e.stopPropagation(); setHovered(true) }}
      onPointerLeave={(e) => { e.stopPropagation(); setHovered(false) }}
    >
      {/* Ground Probe Spike */}
      <mesh position={[0, 0.1, 0]}>
        <cylinderGeometry args={[0.01, 0.01, 0.2, 8]} />
        <meshStandardMaterial color="#cccccc" metalness={0.8} />
      </mesh>
      
      {/* Sensor Main Housing */}
      <mesh position={[0, 0.25, 0]}>
        <cylinderGeometry args={[0.04, 0.04, 0.15, 16]} />
        <meshStandardMaterial color="#222" roughness={0.7} />
      </mesh>
      
      {/* Sensor Top Cap */}
      <mesh position={[0, 0.33, 0]}>
        <sphereGeometry args={[0.04, 16, 16]} />
        <meshStandardMaterial color="#444" />
      </mesh>

      {/* Health Indicator Light */}
      <mesh position={[0, 0.35, 0]}>
        <sphereGeometry args={[0.01, 8, 8]} />
        <meshBasicMaterial color={isHealthy ? "#22c55e" : "#ef4444"} />
      </mesh>
      
      {/* HTML Overlay Label (visible only on hover) */}
      {hovered && (
        <Html position={[0, 0.5, 0]} center zIndexRange={[100, 0]}>
          <div className="flex flex-col gap-1 px-3 py-2 rounded-lg border border-white/10 bg-black/60 backdrop-blur-md shadow-2xl pointer-events-none">
            <div className="flex items-center gap-2">
              <span className="text-blue-400 text-xs">💧</span>
              <span className="text-white text-[10px] font-mono">Moisture</span>
            </div>
            <span className="text-white text-sm font-bold">
              {twin?.substrate_moisture_percent?.toFixed(1) || "74.4"} %
            </span>
            <div className="flex items-center gap-2 mt-1 pt-1 border-t border-white/10">
              <span className="text-rose-400 text-xs">🌡️</span>
              <span className="text-white text-[10px] font-mono">Temperature</span>
            </div>
            <span className="text-white text-xs font-bold">
              {twin?.temperature_c?.toFixed(1) || "26.8"} °C
            </span>
          </div>
        </Html>
      )}
    </group>
  )
}
