"use client"

import { DwarfTomato3D } from "./crops/DwarfTomato3D"

interface CropRendererProps {
  position: [number, number, number]
  length: number
  cropId: string
  twin: any
}

export function Crop3DRenderer({ position, length, cropId, twin }: CropRendererProps) {
  // Switch between different crop implementations based on the backend crop_id
  switch (cropId) {
    case "dwarf_tomato":
      return <DwarfTomato3D position={position} length={length} twin={twin} />
    case "lettuce_looseleaf":
      return <DwarfTomato3D position={position} length={length} twin={twin} /> // Fallback for now
    default:
      return <DwarfTomato3D position={position} length={length} twin={twin} />
  }
}
