"use client"

import { useRef, useMemo, useEffect } from "react"
import * as THREE from "three"

interface DwarfTomatoProps {
  position: [number, number, number]
  length: number
  twin: any
}

export function DwarfTomato3D({ position, length, twin }: DwarfTomatoProps) {
  const stemMesh = useRef<THREE.InstancedMesh>(null)
  const leafMesh = useRef<THREE.InstancedMesh>(null)
  const fruitMesh = useRef<THREE.InstancedMesh>(null)
  const stakeMesh = useRef<THREE.InstancedMesh>(null)
  
  const plantSpacing = 0.5
  const plantCount = Math.floor(length / plantSpacing)
  
  // Geometries
  const stemGeo = useMemo(() => {
    const geo = new THREE.CylinderGeometry(0.02, 0.03, 1.2, 5)
    geo.translate(0, 0.6, 0)
    return geo
  }, [])

  const leafGeo = useMemo(() => {
    const geo = new THREE.ConeGeometry(0.15, 0.4, 4)
    geo.rotateX(-Math.PI / 2)
    geo.translate(0, 0, 0.2) // Translate so base is at origin
    return geo
  }, [])

  const fruitGeo = useMemo(() => {
    return new THREE.SphereGeometry(0.04, 8, 8)
  }, [])
  
  const stakeGeo = useMemo(() => {
    const geo = new THREE.CylinderGeometry(0.01, 0.01, 1.5, 4)
    geo.translate(0, 0.75, 0)
    return geo
  }, [])

  // Materials & Colors based on stress and growth stage
  const stress = twin?.crop_stress_index || 0
  const stage = twin?.growth_stage || "VEGETATIVE"
  
  const stemColor = stress > 0.5 ? "#656220" : "#4ade80"
  const leafColor = stress > 0.5 ? "#84cc16" : "#22c55e"
  const fruitColor = stage === "RIPENING" ? "#ef4444" : "#84cc16"
  
  const leavesPerPlant = 8
  const fruitsPerPlant = (stage === "FRUIT_SET" || stage === "FRUIT_DEVELOPMENT" || stage === "RIPENING") ? 5 : 0

  useEffect(() => {
    if (!stemMesh.current || !leafMesh.current || !stakeMesh.current) return
    
    const dummy = new THREE.Object3D()
    const leafDummy = new THREE.Object3D()
    const fruitDummy = new THREE.Object3D()
    
    // Base plant position iteration
    for (let i = 0; i < plantCount; i++) {
      const z = (i * plantSpacing) - (length / 2)
      
      // Random variations per plant
      const scaleVariation = 0.8 + Math.random() * 0.4
      const rotationVariation = Math.random() * Math.PI * 2
      
      // Stems & Stakes
      dummy.position.set(0, 0.2, z)
      dummy.rotation.set(0, rotationVariation, 0)
      dummy.scale.set(1, scaleVariation, 1)
      dummy.updateMatrix()
      
      stemMesh.current.setMatrixAt(i, dummy.matrix)
      
      // Stake (no rotation, slightly offset)
      dummy.position.set(0.05, 0.2, z - 0.05)
      dummy.rotation.set(0, 0, 0)
      dummy.scale.set(1, 1, 1)
      dummy.updateMatrix()
      stakeMesh.current.setMatrixAt(i, dummy.matrix)
      
      // Leaves
      for (let j = 0; j < leavesPerPlant; j++) {
        const heightPhase = (j / leavesPerPlant) * 1.0 * scaleVariation
        const angle = (j * Math.PI * 0.7) + rotationVariation
        
        // Stress droop
        const droop = stress * 0.5
        
        leafDummy.position.set(0, 0.2 + heightPhase + 0.1, z)
        leafDummy.rotation.set(droop, angle, 0)
        
        // Scale leaf based on height (smaller at top)
        const leafScale = (1 - (j / leavesPerPlant) * 0.5) * scaleVariation
        leafDummy.scale.setScalar(leafScale)
        
        leafDummy.updateMatrix()
        leafMesh.current.setMatrixAt(i * leavesPerPlant + j, leafDummy.matrix)
      }
      
      // Fruits
      if (fruitMesh.current && fruitsPerPlant > 0) {
        for (let k = 0; k < fruitsPerPlant; k++) {
           const heightPhase = 0.4 + (k * 0.1) * scaleVariation
           const angle = (k * Math.PI * 1.3) + rotationVariation
           
           fruitDummy.position.set(
             Math.sin(angle) * 0.05, 
             0.2 + heightPhase, 
             z + Math.cos(angle) * 0.05
           )
           // Drop down slightly (gravity)
           fruitDummy.position.y -= 0.02
           
           // Size variations
           const fruitScale = stage === "RIPENING" ? 1.2 : (stage === "FRUIT_DEVELOPMENT" ? 0.8 : 0.4)
           fruitDummy.scale.setScalar(fruitScale * (0.8 + Math.random() * 0.4))
           
           fruitDummy.updateMatrix()
           fruitMesh.current.setMatrixAt(i * fruitsPerPlant + k, fruitDummy.matrix)
        }
      }
    }
    
    stemMesh.current.instanceMatrix.needsUpdate = true
    leafMesh.current.instanceMatrix.needsUpdate = true
    stakeMesh.current.instanceMatrix.needsUpdate = true
    if (fruitMesh.current) fruitMesh.current.instanceMatrix.needsUpdate = true
    
  }, [plantCount, length, leavesPerPlant, fruitsPerPlant, stress, stage])

  return (
    <group position={position}>
      {/* Substrate/Grow Bag line */}
      <mesh position={[0, 0.1, 0]}>
        <boxGeometry args={[0.4, 0.2, length]} />
        <meshStandardMaterial color="#2d2216" roughness={0.9} />
      </mesh>
      
      {/* Grow bag plastic wrap */}
      <mesh position={[0, 0.101, 0]}>
        <boxGeometry args={[0.41, 0.19, length - 0.02]} />
        <meshStandardMaterial color="#eeeeee" roughness={0.3} metalness={0.1} />
      </mesh>

      <instancedMesh ref={stakeMesh} args={[stakeGeo, undefined, plantCount]}>
        <meshStandardMaterial color="#a3a3a3" roughness={0.6} />
      </instancedMesh>

      <instancedMesh ref={stemMesh} args={[stemGeo, undefined, plantCount]}>
        <meshStandardMaterial color={stemColor} roughness={0.8} />
      </instancedMesh>
      
      <instancedMesh ref={leafMesh} args={[leafGeo, undefined, plantCount * leavesPerPlant]}>
        <meshStandardMaterial color={leafColor} roughness={0.7} side={THREE.DoubleSide} />
      </instancedMesh>
      
      {fruitsPerPlant > 0 && (
        <instancedMesh ref={fruitMesh} args={[fruitGeo, undefined, plantCount * fruitsPerPlant]}>
          <meshStandardMaterial color={fruitColor} roughness={0.3} />
        </instancedMesh>
      )}
    </group>
  )
}
