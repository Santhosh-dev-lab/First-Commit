"use client"

interface ZoneDetailsProps {
  zone: any
  twin: any
}

export function ZoneDetails({ zone, twin }: ZoneDetailsProps) {
  if (!zone) {
    return (
      <div className="h-full flex items-center justify-center text-[10px] font-mono text-white/30 uppercase tracking-widest border border-dashed border-white/10 rounded">
        Select a zone to view details
      </div>
    )
  }

  return (
    <div className="border border-white/10 rounded bg-[#050505] p-6 h-full flex flex-col">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h2 className="text-xl font-mono font-bold tracking-widest">{zone.zone_id.toUpperCase()}</h2>
          <div className="text-[10px] font-mono text-emerald-400 uppercase mt-1 tracking-widest">
            {zone.crop_id.replace("_", " ")}
          </div>
        </div>
        <div className="px-2 py-1 text-[10px] font-mono uppercase bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded">
          {twin?.sensor_health || "HEALTHY"}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-y-6 gap-x-4 flex-1">
        
        <div className="border-b border-white/5 pb-2">
          <span className="block text-[10px] text-white/40 font-mono tracking-widest uppercase mb-1">Temperature</span>
          <span className="font-mono text-lg">{twin?.temperature_c?.toFixed(1) ?? "N/A"} <span className="text-xs text-white/30">°C</span></span>
        </div>
        
        <div className="border-b border-white/5 pb-2">
          <span className="block text-[10px] text-white/40 font-mono tracking-widest uppercase mb-1">Humidity</span>
          <span className="font-mono text-lg">{twin?.humidity_percent?.toFixed(1) ?? "N/A"} <span className="text-xs text-white/30">%</span></span>
        </div>
        
        <div className="border-b border-white/5 pb-2">
          <span className="block text-[10px] text-white/40 font-mono tracking-widest uppercase mb-1">Substrate Moisture</span>
          <span className="font-mono text-lg">{twin?.substrate_moisture_percent?.toFixed(1) ?? "N/A"} <span className="text-xs text-white/30">%</span></span>
        </div>
        
        <div className="border-b border-white/5 pb-2">
          <span className="block text-[10px] text-white/40 font-mono tracking-widest uppercase mb-1">Crop Stress</span>
          <span className={`font-mono text-lg ${(twin?.crop_stress_index ?? 0) > 0.6 ? "text-red-400" : (twin?.crop_stress_index ?? 0) > 0.3 ? "text-amber-400" : "text-emerald-400"}`}>
            {twin?.crop_stress_index?.toFixed(2) ?? "N/A"}
          </span>
        </div>

        <div className="border-b border-white/5 pb-2">
          <span className="block text-[10px] text-white/40 font-mono tracking-widest uppercase mb-1">Irrigation</span>
          <span className={`font-mono text-lg ${twin?.pump_state === "ON" ? "text-blue-400" : "text-white/50"}`}>
            {twin?.pump_state ?? "N/A"}
          </span>
        </div>
        
        <div className="border-b border-white/5 pb-2">
          <span className="block text-[10px] text-white/40 font-mono tracking-widest uppercase mb-1">Growth Stage</span>
          <span className="font-mono text-sm text-emerald-400">{twin?.growth_stage?.replace("_", " ") ?? "N/A"}</span>
        </div>

      </div>
    </div>
  )
}
