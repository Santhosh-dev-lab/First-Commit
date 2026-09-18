"use client"

import { useTwin } from "@/lib/api/client"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { ProvenanceChip } from "@/components/ui/ProvenanceChip"

export function DigitalTwinPanel() {
  const { data: twin, error } = useTwin()

  if (error) return <div className="text-red-500 font-mono text-xs">Failed to load twin</div>
  if (!twin) return <div className="text-white/50 font-mono text-xs">Loading twin state...</div>

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          DIGITAL TWIN
        </CardTitle>
        <ProvenanceChip label="SIMULATED" />
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-6">
          {twin.zones.map((zone, i) => (
            <div key={zone.zone_id} className="border border-white/10 bg-[#0f0f0f] rounded p-4 relative overflow-hidden">
              {/* Subtle grid background for industrial feel */}
              <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none" />
              
              <div className="relative z-10 flex justify-between items-start">
                <div>
                  <h4 className="font-mono text-white/80 font-bold">{zone.zone_id.toUpperCase()}</h4>
                  <p className="font-mono text-xs text-emerald-400 mt-1">{zone.crop_id ? zone.crop_id.replace("_", " ").toUpperCase() : "NO CROP"}</p>
                </div>
                
                <div className="flex gap-4">
                  <div className="text-right">
                    <div className="text-[10px] text-white/40 font-mono uppercase">Area</div>
                    <div className="font-mono text-sm">{zone.area_m2} m²</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] text-white/40 font-mono uppercase">Plants</div>
                    <div className="font-mono text-sm">{zone.plants_count}</div>
                  </div>
                </div>
              </div>

              <div className="relative z-10 grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-white/10">
                <div>
                  <div className="text-[10px] text-white/40 font-mono uppercase mb-1">Local Temp</div>
                  <div className="font-mono">{twin.temperature_c.toFixed(1)}°C</div>
                </div>
                <div>
                  <div className="text-[10px] text-white/40 font-mono uppercase mb-1">Substrate Moist.</div>
                  <div className="font-mono">{twin.substrate_moisture_percent.toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-[10px] text-white/40 font-mono uppercase mb-1">Status</div>
                  <div className="font-mono text-emerald-500">ACTIVE</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
