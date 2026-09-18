"use client"

import { DashboardSnapshot, ZoneSummary } from "@/lib/api/types"
import { Leaf } from "lucide-react"

export function PestDiseaseWidget({ snapshot }: { snapshot: DashboardSnapshot | null }) {
  if (!snapshot) return null;

  return (
    <div className="w-full h-full flex flex-col bg-[#121212]">
      <div className="px-4 py-3 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-sm text-white/90">Crop Health & Stress</h3>
      </div>
      <div className="flex-1 p-0 overflow-auto">
        {snapshot.zones.length === 0 ? (
          <div className="flex items-center justify-center h-full text-white/50 text-sm py-8">
            NO ZONES CONFIGURED
          </div>
        ) : (
          <ul className="divide-y divide-white/5">
            {snapshot.zones.map((zone: ZoneSummary) => (
              <li key={zone.zone_id} className="p-4 hover:bg-white/[0.02] flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${(zone.stress_index ?? 0) > 0.5 ? "bg-orange-500/10 text-orange-500" : "bg-emerald-500/10 text-emerald-500"}`}>
                    <Leaf className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-sm text-white/90 font-medium">{zone.zone_id}</p>
                    <p className="text-xs text-white/50">{zone.crop_id || "Unplanted"}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-medium ${(zone.stress_index ?? 0) > 0.5 ? "text-orange-500" : "text-emerald-500"}`}>
                    Stress: {zone.stress_index != null ? zone.stress_index.toFixed(2) : "N/A"}
                  </p>
                  <p className="text-xs text-white/50">{zone.growth_stage || "N/A"}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

