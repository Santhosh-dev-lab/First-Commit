"use client"

export function FieldMap({ twin }: { twin: any }) {
  return (
    <div className="w-full h-full flex flex-col bg-[#121212]">
      <div className="px-4 py-3 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-sm text-white/90">Field Map – Soil Moisture (%)</h3>
      </div>
      <div className="flex-1 p-4 relative min-h-[300px] flex items-center justify-center">
        <div className="w-full h-full border border-dashed border-white/10 flex items-center justify-center text-white/30 text-sm">
          Map Visualization
        </div>
      </div>
    </div>
  )
}
