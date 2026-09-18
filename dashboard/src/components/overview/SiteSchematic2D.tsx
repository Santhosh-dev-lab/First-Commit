"use client"

interface SiteSchematicProps {
  twin: any
}

export function SiteSchematic2D({ twin }: SiteSchematicProps) {
  const isOnline = !!twin
  const pumpOn = twin?.pump_state === "ON"
  const zones = twin?.zones || []
  const zone1 = zones.find((z: any) => z.zone_id === "zone_1")
  const zone2 = zones.find((z: any) => z.zone_id === "zone_2")

  const getStatusColor = (health: string) => {
    if (health === "CRITICAL") return "bg-red-500/20 border-red-500/50 text-red-400"
    if (health === "WARNING") return "bg-amber-500/20 border-amber-500/50 text-amber-400"
    return "bg-emerald-500/20 border-emerald-500/50 text-emerald-400"
  }
  
  const globalHealthColor = getStatusColor(twin?.sensor_health || "HEALTHY")

  return (
    <div className="w-full flex flex-col md:flex-row gap-6 items-center justify-center py-8">
      
      {/* Infrastructure Node (Water / Pump) */}
      <div className="flex flex-col items-center gap-2">
        <div className="w-32 p-4 border border-blue-500/30 bg-blue-500/5 rounded flex flex-col items-center text-center">
          <div className="text-xl mb-2">🛢️</div>
          <span className="text-[10px] font-mono uppercase text-white/50">Water Tank</span>
          <span className="text-sm font-mono text-blue-400 mt-1">{isOnline ? `${twin?.tank_volume_l?.toFixed(0)} L` : "N/A"}</span>
        </div>
        
        <div className="w-0.5 h-6 bg-white/20 relative">
           {pumpOn && <div className="absolute inset-0 bg-blue-500 animate-pulse" />}
        </div>
        
        <div className={`w-32 p-3 border rounded flex flex-col items-center text-center ${pumpOn ? "border-emerald-500/50 bg-emerald-500/10" : "border-white/10 bg-white/5"}`}>
          <div className="text-xl mb-1">⚙️</div>
          <span className="text-[10px] font-mono uppercase text-white/50">Pump P-01</span>
          <span className={`text-xs font-mono mt-1 font-bold ${pumpOn ? "text-emerald-400" : "text-white/30"}`}>
            {isOnline ? twin?.pump_state : "N/A"}
          </span>
        </div>
      </div>
      
      {/* Connection Pipe */}
      <div className="h-0.5 w-16 md:w-24 bg-white/20 relative hidden md:block">
        {pumpOn && <div className="absolute inset-0 bg-blue-500 animate-pulse" />}
      </div>

      {/* Main Polyhouse Blueprint Node */}
      <div className="flex-1 max-w-2xl border-2 border-white/10 rounded-xl p-6 bg-[#030303] relative">
        <div className="absolute top-4 left-4">
           <span className="text-xs font-mono uppercase text-white/30 tracking-widest">Polyhouse Outline</span>
        </div>
        
        <div className="absolute top-4 right-4">
           <span className={`px-2 py-1 text-[10px] font-mono border rounded ${globalHealthColor}`}>
             SYSTEM: {isOnline ? (twin?.sensor_health || "HEALTHY") : "OFFLINE"}
           </span>
        </div>

        <div className="mt-8 flex flex-col md:flex-row gap-6 h-full">
          {/* Zone 1 */}
          <div className="flex-1 border border-dashed border-white/20 rounded bg-white/[0.02] p-4 flex flex-col justify-between min-h-[250px]">
             <div className="flex justify-between items-start">
               <div>
                 <h3 className="font-mono font-bold text-white tracking-widest">ZONE 01</h3>
                 <span className="text-[10px] font-mono text-emerald-400 uppercase mt-1 block">
                   {isOnline && zone1 ? zone1.crop_id.replace("_", " ") : "N/A"}
                 </span>
               </div>
               {isOnline && (
                 <span className="text-[10px] font-mono text-white/50 border border-white/10 px-1.5 py-0.5 rounded">
                   SENSORS
                 </span>
               )}
             </div>
             
             <div className="grid grid-cols-2 gap-y-4 gap-x-2 mt-6">
                <div>
                  <span className="block text-[10px] text-white/40 uppercase font-mono">Temp</span>
                  <span className="font-mono text-sm">{isOnline ? `${twin.temperature_c.toFixed(1)} °C` : "N/A"}</span>
                </div>
                <div>
                  <span className="block text-[10px] text-white/40 uppercase font-mono">Humidity</span>
                  <span className="font-mono text-sm">{isOnline ? `${twin.humidity_percent.toFixed(1)} %` : "N/A"}</span>
                </div>
                <div>
                  <span className="block text-[10px] text-white/40 uppercase font-mono">Moisture</span>
                  <span className="font-mono text-sm">{isOnline ? `${twin.substrate_moisture_percent.toFixed(1)} %` : "N/A"}</span>
                </div>
                <div>
                  <span className="block text-[10px] text-white/40 uppercase font-mono">Irrigation</span>
                  <span className={`font-mono text-sm font-bold ${pumpOn ? 'text-blue-400' : 'text-white/30'}`}>
                    {isOnline ? (pumpOn ? "FLOWING" : "IDLE") : "N/A"}
                  </span>
                </div>
             </div>
          </div>
          
          {/* Zone 2 */}
          <div className="flex-1 border border-dashed border-white/20 rounded bg-white/[0.02] p-4 flex flex-col justify-between min-h-[250px]">
             <div className="flex justify-between items-start">
               <div>
                 <h3 className="font-mono font-bold text-white tracking-widest">ZONE 02</h3>
                 <span className="text-[10px] font-mono text-emerald-400 uppercase mt-1 block">
                   {isOnline && zone2 ? zone2.crop_id.replace("_", " ") : "N/A"}
                 </span>
               </div>
               {isOnline && (
                 <span className="text-[10px] font-mono text-white/50 border border-white/10 px-1.5 py-0.5 rounded">
                   SENSORS
                 </span>
               )}
             </div>
             
             <div className="grid grid-cols-2 gap-y-4 gap-x-2 mt-6">
                <div>
                  <span className="block text-[10px] text-white/40 uppercase font-mono">Temp</span>
                  <span className="font-mono text-sm">{isOnline ? `${twin.temperature_c.toFixed(1)} °C` : "N/A"}</span>
                </div>
                <div>
                  <span className="block text-[10px] text-white/40 uppercase font-mono">Humidity</span>
                  <span className="font-mono text-sm">{isOnline ? `${twin.humidity_percent.toFixed(1)} %` : "N/A"}</span>
                </div>
                <div>
                  <span className="block text-[10px] text-white/40 uppercase font-mono">Moisture</span>
                  <span className="font-mono text-sm">{isOnline ? `${twin.substrate_moisture_percent.toFixed(1)} %` : "N/A"}</span>
                </div>
                <div>
                  <span className="block text-[10px] text-white/40 uppercase font-mono">Irrigation</span>
                  <span className={`font-mono text-sm font-bold ${pumpOn ? 'text-blue-400' : 'text-white/30'}`}>
                    {isOnline ? (pumpOn ? "FLOWING" : "IDLE") : "N/A"}
                  </span>
                </div>
             </div>
          </div>
        </div>
      </div>

    </div>
  )
}
