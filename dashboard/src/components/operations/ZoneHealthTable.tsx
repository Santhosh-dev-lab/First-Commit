"use client"

import { DashboardSnapshot, ZoneSummary } from "@/lib/api/types"

export function ZoneHealthTable({ snapshot }: { snapshot: DashboardSnapshot | null }) {
  return (
    <div className="w-full h-full flex flex-col bg-[#121212]">
      <div className="px-4 py-3 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-sm text-white/90">Zone Overview</h3>
      </div>
      <div className="flex-1 p-0 overflow-auto">
        <table className="w-full text-xs text-left">
          <thead className="text-white/50 border-b border-white/5 bg-[#1a1a1a]">
            <tr>
              <th className="px-4 py-3 font-medium">ZONE</th>
              <th className="px-4 py-3 font-medium">CROP</th>
              <th className="px-4 py-3 font-medium">GROWTH STAGE</th>
              <th className="px-4 py-3 font-medium">TEMPERATURE</th>
              <th className="px-4 py-3 font-medium">HUMIDITY</th>
              <th className="px-4 py-3 font-medium">MOISTURE</th>
              <th className="px-4 py-3 font-medium">STRESS</th>
              <th className="px-4 py-3 font-medium">IRRIGATION</th>
              <th className="px-4 py-3 font-medium">SENSOR HEALTH</th>
              <th className="px-4 py-3 font-medium">STATUS</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-white/90">
            {!snapshot ? (
              <tr>
                <td colSpan={10} className="px-4 py-8 text-center text-white/50">WAITING FOR DATA</td>
              </tr>
            ) : snapshot.zones.length === 0 ? (
              <tr>
                <td colSpan={10} className="px-4 py-8 text-center text-white/50">NO ZONES CONFIGURED</td>
              </tr>
            ) : (
              snapshot.zones.map((zone: ZoneSummary) => (
                <tr key={zone.zone_id} className="hover:bg-white/[0.02]">
                  <td className="px-4 py-3 font-medium">{zone.zone_id}</td>
                  <td className="px-4 py-3 text-white/70">{zone.crop_id || "N/A"}</td>
                  <td className="px-4 py-3 text-white/70">{zone.growth_stage || "N/A"}</td>
                  <td className="px-4 py-3 text-white/70">{zone.temperature_c != null ? `${zone.temperature_c.toFixed(1)}°C` : "N/A"}</td>
                  <td className="px-4 py-3 text-white/70">{zone.humidity_percent != null ? `${zone.humidity_percent.toFixed(1)}%` : "N/A"}</td>
                  <td className="px-4 py-3 text-white/70">{zone.moisture_percent != null ? `${zone.moisture_percent.toFixed(1)}%` : "N/A"}</td>
                  <td className={`px-4 py-3 ${(zone.stress_index ?? 0) > 0.5 ? "text-orange-500" : "text-emerald-500"}`}>{zone.stress_index != null ? zone.stress_index.toFixed(2) : "N/A"}</td>
                  <td className={`px-4 py-3 ${(zone.irrigation_status === "ON") ? "text-emerald-500" : "text-white/50"}`}>{zone.irrigation_status || "N/A"}</td>
                  <td className={`px-4 py-3 ${zone.sensor_health === "HEALTHY" ? "text-emerald-500" : "text-red-500"}`}>{zone.sensor_health || "N/A"}</td>
                  <td className="px-4 py-3 text-emerald-500">{zone.status || "N/A"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

