"use client"

export function ZoneHealthTable({ twin }: { twin: any }) {
  return (
    <div className="w-full h-full flex flex-col bg-[#121212]">
      <div className="px-4 py-3 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-sm text-white/90">Soil Health - Zone Overview</h3>
      </div>
      <div className="flex-1 p-0 overflow-auto">
        <table className="w-full text-xs text-left">
          <thead className="text-white/50 border-b border-white/5">
            <tr>
              <th className="px-4 py-3 font-medium">Zone</th>
              <th className="px-4 py-3 font-medium">pH</th>
              <th className="px-4 py-3 font-medium">EC (dS/m)</th>
              <th className="px-4 py-3 font-medium">N (kg/ha)</th>
              <th className="px-4 py-3 font-medium">P (kg/ha)</th>
              <th className="px-4 py-3 font-medium">K (kg/ha)</th>
              <th className="px-4 py-3 font-medium">Temp (°C)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-white/90">
            {/* Rows will go here */}
          </tbody>
        </table>
      </div>
    </div>
  )
}
