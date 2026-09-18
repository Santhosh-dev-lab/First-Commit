"use client"

import { useRef, useMemo, useEffect } from "react"
import * as THREE from "three"

interface CropRowProps {
  position: [number, number, number]
  length: number
  twin: any
}

export function CropRow3D({ position, length, twin }: CropRowProps) {
  const meshRef = useRef<THREE.InstancedMesh>(null)
  
  const plantCount = Math.floor(length / 0.5) // 1 plant every 0.5 units
  
  // Create a base procedural plant geometry: a stem + simple canopy
  const geometry = useMemo(() => {
    const geo = new THREE.CylinderGeometry(0.2, 0.1, 0.8, 5)
    geo.translate(0, 0.4, 0)
    return geo
  }, [])

  // Material changes based on stress
  const stress = twin?.crop_stress_index || 0
  const color = useMemo(() => {
    if (stress > 0.6) return new THREE.Color("#d97706") // High stress - yellow/orange
    if (stress > 0.3) return new THREE.Color("#84cc16") // Mild stress - light green
    return new THREE.Color("#22c55e") // Healthy - vibrant green
  }, [stress])

  useEffect(() => {
    if (!meshRef.current) return
    
    const dummy = new THREE.Object3D()
    
    for (let i = 0; i < plantCount; i++) {
      // distribute along z-axis centered on the row
      const z = (i * 0.5) - (length / 2)
      
      // slight random rotation/scale for organic feel
      dummy.position.set(0, 0, z)
      dummy.rotation.y = Math.random() * Math.PI
      dummy.scale.setScalar(0.8 + Math.random() * 0.4)
      
      dummy.updateMatrix()
      meshRef.current.setMatrixAt(i, dummy.matrix)
    }
    
    meshRef.current.instanceMatrix.needsUpdate = true
  }, [plantCount, length])

  return (
    <group position={position}>
      {/* Substrate/Grow Bag line */}
      <mesh position={[0, 0.1, 0]}>
        <boxGeometry args={[0.6, 0.2, length]} />
        <meshStandardMaterial color="#3f2e1c" roughness={0.9} />
      </mesh>

      {/* Instanced Plants */}
      <instancedMesh ref={meshRef} args={[geometry, undefined, plantCount]} position={[0, 0.2, 0]}>
        <meshStandardMaterial color={color} roughness={0.8} />
      </instancedMesh>
    </group>
  )
}
