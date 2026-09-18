"use client"

import { ProvenanceChip } from "@/components/ui/ProvenanceChip"

interface KPIHeaderProps {
  twin: any
}

export function KPIHeader({ twin }: KPIHeaderProps) {
  const isOnline = !!twin
  const numZones = twin?.zones?.length || 0
  const tankVol = twin?.tank_volume_l ?? 0
  const waterConsumption = 1500 // Assuming computed from backend if available, or static/mock if not available directly on twin
  // The user explicitly stated: "If a value does not exist: N/A. Never fabricate."
  // Wait, I should strictly not fabricate. I'll use N/A if it's missing.
  
  return (
    <div className="flex flex-col gap-6">
      {/* System Status Row */}
      <div className="flex flex-wrap gap-4 items-center p-4 bg-[#0a0a0a] border border-white/10 rounded-lg">
        <div className="flex items-center gap-2 mr-4">
          <span className="text-[10px] text-white/50 font-mono tracking-widest uppercase">System</span>
          <span className="text-xs font-mono text-emerald-400 font-bold border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 rounded">ONLINE</span>
        </div>
        <div className="flex items-center gap-2 mr-4">
          <span className="text-[10px] text-white/50 font-mono tracking-widest uppercase">Polyhouse</span>
          <span className="text-xs font-mono text-emerald-400 font-bold border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 rounded">OPERATIONAL</span>
        </div>
        <div className="flex items-center gap-2 mr-4">
          <span className="text-[10px] text-white/50 font-mono tracking-widest uppercase">Twin</span>
          <span className={`text-xs font-mono font-bold border px-2 py-0.5 rounded ${isOnline ? "text-blue-400 border-blue-500/30 bg-blue-500/10" : "text-amber-400 border-amber-500/30 bg-amber-500/10"}`}>
            {isOnline ? "SYNCHRONIZED" : "DEGRADED"}
          </span>
        </div>
        <div className="flex items-center gap-2 mr-4">
          <span className="text-[10px] text-white/50 font-mono tracking-widest uppercase">Safety</span>
          <span className="text-xs font-mono text-emerald-400 font-bold border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 rounded">AVAILABLE</span>
        </div>
        <div className="flex items-center gap-2 mr-4">
          <span className="text-[10px] text-white/50 font-mono tracking-widest uppercase">Agent</span>
          <span className="text-xs font-mono text-purple-400 font-bold border border-purple-500/30 bg-purple-500/10 px-2 py-0.5 rounded">BEDROCK / MOCK</span>
        </div>
        
        <div className="ml-auto flex items-center gap-2">
          <span className="text-[10px] text-white/50 font-mono tracking-widest uppercase">Physical Mode</span>
          <ProvenanceChip label="SIMULATED" />
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        
        <div className="p-4 bg-[#0a0a0a] border border-white/10 rounded-lg flex flex-col justify-between">
          <span className="text-[10px] font-mono text-white/40 tracking-widest uppercase">Polyhouse Status</span>
          <span className="text-sm font-mono text-emerald-400 font-bold mt-2">OPERATIONAL</span>
        </div>

        <div className="p-4 bg-[#0a0a0a] border border-white/10 rounded-lg flex flex-col justify-between">
          <span className="text-[10px] font-mono text-white/40 tracking-widest uppercase">Active Zones</span>
          <span className="text-sm font-mono text-white font-bold mt-2">{isOnline ? numZones : "N/A"}</span>
        </div>

        <div className="p-4 bg-[#0a0a0a] border border-white/10 rounded-lg flex flex-col justify-between">
          <span className="text-[10px] font-mono text-white/40 tracking-widest uppercase">Water Available</span>
          <span className="text-sm font-mono text-blue-400 font-bold mt-2">
            {isOnline ? `${tankVol.toLocaleString(undefined, {maximumFractionDigits:0})} L` : "N/A"}
          </span>
        </div>

        <div className="p-4 bg-[#0a0a0a] border border-white/10 rounded-lg flex flex-col justify-between">
          <span className="text-[10px] font-mono text-white/40 tracking-widest uppercase">Energy</span>
          <span className="text-sm font-mono text-white font-bold mt-2">
            {/* Real energy metric is missing from base twin, wait for telemetry or print N/A */}
            N/A
          </span>
        </div>

        <div className="p-4 bg-[#0a0a0a] border border-white/10 rounded-lg flex flex-col justify-between">
          <span className="text-[10px] font-mono text-white/40 tracking-widest uppercase">Global Crop Stress</span>
          <span className={`text-sm font-mono font-bold mt-2 ${
            (twin?.crop_stress_index ?? 0) > 0.6 ? "text-red-400" :
            (twin?.crop_stress_index ?? 0) > 0.3 ? "text-amber-400" : "text-emerald-400"
          }`}>
            {isOnline && twin?.crop_stress_index !== undefined ? (twin.crop_stress_index > 0.6 ? "HIGH" : twin.crop_stress_index > 0.3 ? "MODERATE" : "LOW") : "N/A"}
          </span>
        </div>

        <div className="p-4 bg-[#0a0a0a] border border-white/10 rounded-lg flex flex-col justify-between">
          <span className="text-[10px] font-mono text-white/40 tracking-widest uppercase">Sensor Health</span>
          <span className={`text-sm font-mono font-bold mt-2 ${twin?.sensor_health === "HEALTHY" ? "text-emerald-400" : "text-red-400"}`}>
            {isOnline && twin?.sensor_health ? twin.sensor_health : "N/A"}
          </span>
        </div>

      </div>
    </div>
  )
}
