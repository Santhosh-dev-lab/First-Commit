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

  const formatVal = (val: number | null | undefined, unit: string = "") => {
    if (!isOnline || val === null || val === undefined) return "N/A"
    return `${val.toFixed(1)} ${unit}`.trim()
  }

  return (
    <div className="w-full h-full min-h-[400px] flex items-center justify-center p-4">
      {/* Blueprint Container */}
      <div className="w-full max-w-4xl border-2 border-white/20 rounded-xl bg-[#030303] relative p-8 shadow-2xl overflow-hidden flex flex-col">
        
        {/* Background Grid */}
        <div className="absolute inset-0 opacity-[0.04]" style={{ backgroundImage: 'linear-gradient(white 1px, transparent 1px), linear-gradient(90deg, white 1px, transparent 1px)', backgroundSize: '30px 30px', backgroundPosition: 'center center' }}></div>

        {/* Header */}
        <div className="flex justify-between items-start relative z-10 mb-8">
          <div>
            <h2 className="text-sm font-mono tracking-[0.2em] text-white/50 uppercase">Floor Plan</h2>
            <h1 className="text-2xl font-light text-white tracking-widest mt-1">POLYHOUSE MAIN</h1>
          </div>
          <div className={`px-3 py-1.5 border rounded-sm font-mono text-xs tracking-widest ${isOnline ? 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10' : 'border-red-500/30 text-red-400 bg-red-500/10'}`}>
            SYSTEM: {isOnline ? (twin?.sensor_health || "HEALTHY") : "OFFLINE"}
          </div>
        </div>

        {/* Zones Container */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
          
          {/* Zone 1 */}
          <div className="border border-white/20 bg-emerald-900/10 rounded-lg p-6 relative group overflow-hidden flex flex-col">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent pointer-events-none" />
            
            <div className="flex justify-between items-start mb-6 relative z-10">
              <div>
                <h3 className="font-mono text-lg font-bold text-white tracking-widest">ZONE 01</h3>
                <span className="font-mono text-[10px] text-emerald-400 uppercase tracking-widest mt-1 block">
                  {isOnline && zone1 ? zone1.crop_id.replace("_", " ") : "WAITING FOR DATA"}
                </span>
              </div>
              <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]"></div>
            </div>

            {/* Simulated Crop Rows */}
            <div className="flex-1 flex flex-col justify-center gap-3 opacity-30 py-4 relative z-10">
              <div className="h-1.5 w-full bg-emerald-500 rounded-full" />
              <div className="h-1.5 w-full bg-emerald-500 rounded-full" />
              <div className="h-1.5 w-full bg-emerald-500 rounded-full" />
              <div className="h-1.5 w-full bg-emerald-500 rounded-full" />
            </div>

            {/* Zone Data Overlay */}
            <div className="grid grid-cols-2 gap-4 mt-6 relative z-10 bg-black/40 p-4 rounded border border-white/5 backdrop-blur-sm">
              <div>
                <span className="block text-[9px] text-white/40 uppercase font-mono tracking-widest">Temp</span>
                <span className="font-mono text-sm text-white">{formatVal(zone1?.temperature_c, "°C")}</span>
              </div>
              <div>
                <span className="block text-[9px] text-white/40 uppercase font-mono tracking-widest">Humidity</span>
                <span className="font-mono text-sm text-white">{formatVal(zone1?.humidity_percent, "%")}</span>
              </div>
              <div>
                <span className="block text-[9px] text-white/40 uppercase font-mono tracking-widest">Moisture</span>
                <span className="font-mono text-sm text-white">{formatVal(zone1?.substrate_moisture_percent, "%")}</span>
              </div>
              <div>
                <span className="block text-[9px] text-white/40 uppercase font-mono tracking-widest">VPD</span>
                <span className="font-mono text-sm text-white">{formatVal(zone1?.vpd_kpa, "kPa")}</span>
              </div>
            </div>
          </div>

          {/* Zone 2 */}
          <div className="border border-white/20 bg-emerald-900/10 rounded-lg p-6 relative group overflow-hidden flex flex-col">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent pointer-events-none" />
            
            <div className="flex justify-between items-start mb-6 relative z-10">
              <div>
                <h3 className="font-mono text-lg font-bold text-white tracking-widest">ZONE 02</h3>
                <span className="font-mono text-[10px] text-emerald-400 uppercase tracking-widest mt-1 block">
                  {isOnline && zone2 ? zone2.crop_id.replace("_", " ") : "WAITING FOR DATA"}
                </span>
              </div>
              <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]"></div>
            </div>

            {/* Simulated Crop Rows */}
            <div className="flex-1 flex flex-col justify-center gap-3 opacity-30 py-4 relative z-10">
              <div className="h-1.5 w-full bg-emerald-500 rounded-full" />
              <div className="h-1.5 w-full bg-emerald-500 rounded-full" />
              <div className="h-1.5 w-full bg-emerald-500 rounded-full" />
              <div className="h-1.5 w-full bg-emerald-500 rounded-full" />
            </div>

            {/* Zone Data Overlay */}
            <div className="grid grid-cols-2 gap-4 mt-6 relative z-10 bg-black/40 p-4 rounded border border-white/5 backdrop-blur-sm">
              <div>
                <span className="block text-[9px] text-white/40 uppercase font-mono tracking-widest">Temp</span>
                <span className="font-mono text-sm text-white">{formatVal(zone2?.temperature_c, "°C")}</span>
              </div>
              <div>
                <span className="block text-[9px] text-white/40 uppercase font-mono tracking-widest">Humidity</span>
                <span className="font-mono text-sm text-white">{formatVal(zone2?.humidity_percent, "%")}</span>
              </div>
              <div>
                <span className="block text-[9px] text-white/40 uppercase font-mono tracking-widest">Moisture</span>
                <span className="font-mono text-sm text-white">{formatVal(zone2?.substrate_moisture_percent, "%")}</span>
              </div>
              <div>
                <span className="block text-[9px] text-white/40 uppercase font-mono tracking-widest">VPD</span>
                <span className="font-mono text-sm text-white">{formatVal(zone2?.vpd_kpa, "kPa")}</span>
              </div>
            </div>
          </div>
          
        </div>

        {/* Infrastructure Footer */}
        <div className="mt-8 pt-6 border-t border-white/10 relative z-10 flex items-center gap-6">
          <div className="flex items-center gap-4 bg-black/40 p-3 rounded border border-white/5 backdrop-blur-sm">
             <div className="w-8 h-8 rounded bg-blue-500/20 border border-blue-500/50 flex items-center justify-center text-blue-400">
               🛢️
             </div>
             <div>
               <span className="block text-[9px] font-mono tracking-widest uppercase text-white/50">Main Tank</span>
               <span className="font-mono text-sm text-white">
                 {isOnline && twin?.tank_volume_l !== undefined ? `${twin.tank_volume_l.toFixed(0)} L` : "N/A"}
               </span>
             </div>
          </div>

          <div className="flex-1 h-px bg-white/20 relative">
             {pumpOn && <div className="absolute inset-0 bg-blue-500 animate-pulse" />}
          </div>

          <div className="flex items-center gap-4 bg-black/40 p-3 rounded border border-white/5 backdrop-blur-sm">
             <div className={`w-8 h-8 rounded border flex items-center justify-center ${pumpOn ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400' : 'bg-white/5 border-white/20 text-white/50'}`}>
               ⚙️
             </div>
             <div>
               <span className="block text-[9px] font-mono tracking-widest uppercase text-white/50">Pump P-01</span>
               <span className={`font-mono text-sm font-bold ${pumpOn ? 'text-emerald-400' : 'text-white/50'}`}>
                 {isOnline ? twin?.pump_state : "N/A"}
               </span>
             </div>
          </div>
        </div>

      </div>
    </div>
  )
}
