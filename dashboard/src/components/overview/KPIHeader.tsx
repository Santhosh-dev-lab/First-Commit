"use client"

import { Droplet, Activity, Zap, Target, Leaf, HeartPulse } from "lucide-react"
import { DashboardSnapshot } from "@/lib/api/types"

interface KPIHeaderProps {
  snapshot: DashboardSnapshot | null
}

export function KPIHeader({ snapshot }: KPIHeaderProps) {
  if (!snapshot) {
    return <div className="h-28 flex items-center justify-center text-white/50 text-sm">WAITING FOR DATA</div>
  }

  const zones = snapshot.zones
  const activeZones = zones.filter(z => z.status === "ONLINE").length
  const avgMoisture = zones.reduce((acc, z) => acc + (z.moisture_percent || 0), 0) / (zones.length || 1)
  const isIrrigating = zones.some(z => z.irrigation_status === "ON") || snapshot.system.digital_twin === "IRRIGATING" // simplistic check
  const waterAvailable = snapshot.resources.remaining_water_l ?? 0
  const avgStress = zones.reduce((acc, z) => acc + (z.stress_index || 0), 0) / (zones.length || 1)
  const allSensorsHealthy = zones.every(z => z.sensor_health === "HEALTHY")

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
      
      {/* 1. Active Zones */}
      <div className="p-4 bg-[#121212] border border-white/5 rounded-xl flex flex-col justify-between h-28 relative overflow-hidden">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-emerald-500/10 rounded-full shrink-0 mt-1">
            <Target className="w-5 h-5 text-emerald-500" />
          </div>
          <div>
            <h3 className="text-[11px] font-medium text-white/70">Active Zones</h3>
            <p className="text-xl font-medium text-white mt-0.5">{activeZones} <span className="text-sm text-white/50 font-normal">of {zones.length}</span></p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
          {activeZones === zones.length ? "All zones online" : "Degraded"}
        </div>
      </div>

      {/* 2. Avg Soil Moisture */}
      <div className="p-4 bg-[#121212] border border-white/5 rounded-xl flex flex-col justify-between h-28 relative overflow-hidden">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-500/10 rounded-full shrink-0 mt-1">
            <Droplet className="w-5 h-5 text-blue-500" />
          </div>
          <div>
            <h3 className="text-[11px] font-medium text-white/70">Avg Soil Moisture</h3>
            <p className="text-xl font-medium text-white mt-0.5">{avgMoisture.toFixed(1)}%</p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
          Derived from zone state
        </div>
      </div>

      {/* 3. Irrigation Status */}
      <div className="p-4 bg-[#121212] border border-white/5 rounded-xl flex flex-col justify-between h-28 relative overflow-hidden">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-purple-500/10 rounded-full shrink-0 mt-1">
            <Zap className="w-5 h-5 text-purple-500" />
          </div>
          <div>
            <h3 className="text-[11px] font-medium text-white/70">Irrigation Status</h3>
            <p className={`text-xl font-medium mt-0.5 ${isIrrigating ? "text-emerald-500" : "text-white"}`}>{isIrrigating ? "ACTIVE" : "IDLE"}</p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className={`w-1.5 h-1.5 rounded-full ${isIrrigating ? "bg-emerald-500" : "bg-white/50"}`}></div>
          Actuator state
        </div>
      </div>

      {/* 4. Water Available */}
      <div className="p-4 bg-[#121212] border border-white/5 rounded-xl flex flex-col justify-between h-28 relative overflow-hidden">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-500/10 rounded-full shrink-0 mt-1">
            <Droplet className="w-5 h-5 text-blue-500" />
          </div>
          <div>
            <h3 className="text-[11px] font-medium text-white/70">Water Available</h3>
            <p className="text-xl font-medium text-white mt-0.5">{waterAvailable.toFixed(0)} <span className="text-sm text-white/50 font-normal">L</span></p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
          Main tank reserve
        </div>
      </div>

      {/* 5. Crop Stress */}
      <div className="p-4 bg-[#121212] border border-white/5 rounded-xl flex flex-col justify-between h-28 relative overflow-hidden">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-orange-500/10 rounded-full shrink-0 mt-1">
            <Leaf className="w-5 h-5 text-orange-500" />
          </div>
          <div>
            <h3 className="text-[11px] font-medium text-white/70">Avg Crop Stress</h3>
            <p className={`text-xl font-medium mt-0.5 ${avgStress > 0.5 ? "text-orange-500" : "text-emerald-500"}`}>{avgStress.toFixed(2)}</p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className={`w-1.5 h-1.5 rounded-full ${avgStress > 0.5 ? "bg-orange-500" : "bg-emerald-500"}`}></div>
          Physiological model
        </div>
      </div>

      {/* 6. Sensor Health */}
      <div className="p-4 bg-[#121212] border border-white/5 rounded-xl flex flex-col justify-between h-28 relative overflow-hidden">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-emerald-500/10 rounded-full shrink-0 mt-1">
            <HeartPulse className="w-5 h-5 text-emerald-500" />
          </div>
          <div>
            <h3 className="text-[11px] font-medium text-white/70">Sensor Health</h3>
            <p className={`text-xl font-medium mt-0.5 ${allSensorsHealthy ? "text-emerald-500" : "text-red-500"}`}>{allSensorsHealthy ? "NOMINAL" : "DEGRADED"}</p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className={`w-1.5 h-1.5 rounded-full ${allSensorsHealthy ? "bg-emerald-500" : "bg-red-500"}`}></div>
          Edge gateway status
        </div>
      </div>

    </div>
  )
}
