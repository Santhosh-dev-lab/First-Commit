"use client"

import { useMemo } from "react"
import * as THREE from "three"

export function PolyhouseStructure({ inspectionMode = false }: { inspectionMode?: boolean }) {
  const frameMaterial = useMemo(() => new THREE.MeshStandardMaterial({ 
    color: "#b0b4b8", 
    metalness: 0.9, 
    roughness: 0.4 
  }), [])
  
  const glassMaterial = useMemo(() => new THREE.MeshPhysicalMaterial({ 
    color: "#ffffff", 
    transparent: true, 
    opacity: inspectionMode ? 0.05 : 0.35, 
    roughness: 0.05,
    transmission: inspectionMode ? 0.99 : 0.95,
    thickness: 0.05,
    ior: 1.5,
    side: THREE.DoubleSide
  }), [inspectionMode])

  const width = 16
  const length = 24
  const wallHeight = 4
  const roofRadius = width / 2
  
  const numArches = 9
  const archSpacing = length / (numArches - 1)

  return (
    <group position={[0, 0, 0]}>
      {/* Concrete Foundation Perimeter */}
      <mesh position={[0, 0.25, 0]} receiveShadow castShadow>
        <boxGeometry args={[width + 0.4, 0.5, length + 0.4]} />
        <meshStandardMaterial color="#8a8d8f" roughness={0.9} />
      </mesh>
      
      {/* Interior Floor (Gravel/Soil with Walkway) */}
      <mesh position={[0, 0.51, 0]} receiveShadow>
        <planeGeometry args={[width, length]} />
        <meshStandardMaterial color="#3c3732" roughness={1} />
        <group rotation={[-Math.PI / 2, 0, 0]} />
      </mesh>
      
      {/* Central Concrete Walkway */}
      <mesh position={[0, 0.52, 0]} receiveShadow rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[2, length]} />
        <meshStandardMaterial color="#7a7d7f" roughness={0.8} />
      </mesh>

      {/* Main Glass Walls */}
      <mesh position={[0, wallHeight / 2 + 0.5, 0]} castShadow receiveShadow>
        <boxGeometry args={[width, wallHeight, length]} />
        <primitive object={glassMaterial} attach="material" />
      </mesh>

      {/* Arched Glass Roof */}
      <mesh position={[0, wallHeight + 0.5, 0]} rotation={[0, 0, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[roofRadius, roofRadius, length, 32, 1, false, 0, Math.PI]} />
        <primitive object={glassMaterial} attach="material" />
        <group rotation={[Math.PI / 2, 0, 0]} />
      </mesh>

      {/* Structural Hoops / Arches */}
      {Array.from({ length: numArches }).map((_, i) => {
        const z = (i * archSpacing) - (length / 2)
        return (
          <group key={i} position={[0, 0, z]}>
            {/* Left Post */}
            <mesh position={[-width/2, wallHeight/2 + 0.5, 0]} castShadow>
              <cylinderGeometry args={[0.06, 0.06, wallHeight]} />
              <primitive object={frameMaterial} attach="material" />
            </mesh>
            {/* Right Post */}
            <mesh position={[width/2, wallHeight/2 + 0.5, 0]} castShadow>
              <cylinderGeometry args={[0.06, 0.06, wallHeight]} />
              <primitive object={frameMaterial} attach="material" />
            </mesh>
            {/* Roof Arch */}
            <mesh position={[0, wallHeight + 0.5, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
              <torusGeometry args={[roofRadius, 0.06, 8, 48, Math.PI]} />
              <primitive object={frameMaterial} attach="material" />
            </mesh>
            
            {/* Horizontal Cross Tie (Collar tie) */}
            <mesh position={[0, wallHeight + 1.5, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
              <cylinderGeometry args={[0.04, 0.04, width - 2]} />
              <primitive object={frameMaterial} attach="material" />
            </mesh>
          </group>
        )
      })}
      
      {/* Longitudinal Purlins */}
      <mesh position={[0, wallHeight + roofRadius + 0.5, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.06, length]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>
      
      <mesh position={[-roofRadius * 0.7, wallHeight + roofRadius * 0.7 + 0.5, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.05, 0.05, length]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>
      
      <mesh position={[roofRadius * 0.7, wallHeight + roofRadius * 0.7 + 0.5, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.05, 0.05, length]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>

      <mesh position={[-width/2, wallHeight + 0.5, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.06, length]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>
      
      <mesh position={[width/2, wallHeight + 0.5, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.06, length]} />
        <primitive object={frameMaterial} attach="material" />
      </mesh>

      {/* End Wall Framing (Front) */}
      <group position={[0, 0, length / 2]}>
        <mesh position={[-2, wallHeight/2 + 0.5, 0]} castShadow>
          <cylinderGeometry args={[0.06, 0.06, wallHeight]} />
          <primitive object={frameMaterial} attach="material" />
        </mesh>
        <mesh position={[2, wallHeight/2 + 0.5, 0]} castShadow>
          <cylinderGeometry args={[0.06, 0.06, wallHeight]} />
          <primitive object={frameMaterial} attach="material" />
        </mesh>
        <mesh position={[0, 2, 0]} castShadow>
          {/* Door Header */}
          <boxGeometry args={[4, 0.1, 0.1]} />
          <primitive object={frameMaterial} attach="material" />
        </mesh>
        {/* Door */}
        <mesh position={[0, 1.25, 0]} castShadow>
          <boxGeometry args={[4, 2.5, 0.05]} />
          <meshStandardMaterial color="#333333" metalness={0.5} roughness={0.8} />
        </mesh>
      </group>
      
      {/* End Wall Framing (Back) */}
      <group position={[0, 0, -length / 2]}>
        <mesh position={[-width/4, wallHeight/2 + 0.5, 0]} castShadow>
          <cylinderGeometry args={[0.06, 0.06, wallHeight + 1]} />
          <primitive object={frameMaterial} attach="material" />
        </mesh>
        <mesh position={[width/4, wallHeight/2 + 0.5, 0]} castShadow>
          <cylinderGeometry args={[0.06, 0.06, wallHeight + 1]} />
          <primitive object={frameMaterial} attach="material" />
        </mesh>
      </group>

    </group>
  )
}
