"use client"

import { useState } from "react"
import * as THREE from "three"
import { Html } from "@react-three/drei"
import { Crop3DRenderer } from "./Crop3DRenderer"
import { Sensor3D } from "./Sensor3D"

interface Zone3DProps {
  zone: any
  index: number
  twin: any
  onSelect: () => void
}

export function Zone3D({ zone, index, twin, onSelect }: Zone3DProps) {
  const [hovered, setHovered] = useState(false)
  
  // Arrange zones side by side. 
  // Assuming total polyhouse width 12, length 16. 
  // Two zones split the length: Zone 1 at z = -4, Zone 2 at z = 4
  const zPosition = index === 0 ? -4 : 4
  const width = 10
  const length = 7

  return (
    <group position={[0, 0, zPosition]}>
      {/* Interactive Zone Floor */}
      <mesh 
        position={[0, 0.52, 0]} 
        rotation={[-Math.PI / 2, 0, 0]} 
        onClick={(e) => { e.stopPropagation(); onSelect() }}
        onPointerOver={(e) => { e.stopPropagation(); setHovered(true) }}
        onPointerOut={(e) => { e.stopPropagation(); setHovered(false) }}
      >
        <planeGeometry args={[width, length]} />
        <meshBasicMaterial 
          color={hovered ? "#3b82f6" : "#224422"} 
          transparent 
          opacity={hovered ? 0.2 : 0.05} 
          side={2}
        />
      </mesh>

      {/* Zone Outline */}
      <lineSegments position={[0, 0.53, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <edgesGeometry args={[new THREE.PlaneGeometry(width, length)]} />
        <lineBasicMaterial color={hovered ? "#60a5fa" : "#22c55e"} transparent opacity={0.3} />
      </lineSegments>

      {/* HTML Zone Label Overlay */}
      <Html position={[0, 4, 0]} center zIndexRange={[100, 0]}>
        <div 
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 bg-black/60 backdrop-blur-md cursor-pointer hover:bg-black/80 transition-colors shadow-2xl"
          onClick={(e) => { e.stopPropagation(); onSelect() }}
          onPointerEnter={() => setHovered(true)}
          onPointerLeave={() => setHovered(false)}
        >
          <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
          <div className="flex flex-col">
            <span className="text-white text-xs font-bold tracking-wider">{zone.zone_id.toUpperCase()}</span>
            <span className="text-white/60 text-[10px] font-mono">{zone.crop_id?.replace("_", " ") || "No Crop"}</span>
          </div>
        </div>
      </Html>

      {/* Crop Rows & Beds */}
      {/* 5 rows per zone with proper bed structure */}
      <Crop3DRenderer position={[-3, 0.51, 0]} length={length - 2} cropId={zone.crop_id} twin={twin} />
      <Crop3DRenderer position={[-1.5, 0.51, 0]} length={length - 2} cropId={zone.crop_id} twin={twin} />
      <Crop3DRenderer position={[0, 0.51, 0]} length={length - 2} cropId={zone.crop_id} twin={twin} />
      <Crop3DRenderer position={[1.5, 0.51, 0]} length={length - 2} cropId={zone.crop_id} twin={twin} />
      <Crop3DRenderer position={[3, 0.51, 0]} length={length - 2} cropId={zone.crop_id} twin={twin} />

      {/* Sensors */}
      <Sensor3D position={[width/2 - 1, 0.51, 0]} health={twin?.sensor_health || "HEALTHY"} twin={twin} />

    </group>
  )
}
