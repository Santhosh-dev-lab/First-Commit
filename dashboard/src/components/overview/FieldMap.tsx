"use client"

import { DashboardSnapshot, ZoneSummary } from "@/lib/api/types"

export function FieldMap({ snapshot }: { snapshot: DashboardSnapshot | null }) {
  if (!snapshot) {
    return <div className="w-full h-full bg-[#121212] flex items-center justify-center text-white/50 text-sm">WAITING FOR DATA</div>
  }

  return (
    <div className="w-full h-full flex flex-col bg-[#121212]">
      <div className="px-4 py-3 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-sm text-white/90">Field Map – Soil Moisture (%)</h3>
      </div>
      <div className="flex-1 p-4 relative min-h-[300px] flex gap-2">
        {snapshot.zones.length === 0 ? (
          <div className="w-full h-full flex items-center justify-center text-white/30 text-sm">NO ZONES CONFIGURED</div>
        ) : (
          snapshot.zones.map((zone: ZoneSummary) => {
            const moisture = zone.moisture_percent ?? 0;
            const bgClass = moisture > 50 ? "bg-blue-500/20" : moisture > 30 ? "bg-emerald-500/20" : "bg-orange-500/20";
            const borderClass = moisture > 50 ? "border-blue-500/50" : moisture > 30 ? "border-emerald-500/50" : "border-orange-500/50";
            return (
              <div key={zone.zone_id} className={`flex-1 flex flex-col items-center justify-center border ${bgClass} ${borderClass} rounded-lg relative`}>
                <div className="absolute top-2 left-2 text-xs font-medium text-white/70">{zone.zone_id}</div>
                <div className="text-2xl font-bold text-white">{moisture.toFixed(1)}%</div>
                <div className="text-[10px] text-white/50">{zone.crop_id || "Unplanted"}</div>
              </div>
            );
          })
        )}
      </div>
    </div>
  )
}

