"use client"

import { useState } from "react"
import { Header } from "@/components/dashboard/Header"
import { PolyhouseScene } from "@/components/polyhouse3d/PolyhouseScene"
import { SidebarNav } from "@/components/dashboard/SidebarNav"
import { useTwin } from "@/lib/api/client"
import { ProvenanceChip } from "@/components/ui/ProvenanceChip"

export default function TwinPage() {
  const [selectedZone, setSelectedZone] = useState<string | null>(null)
  const { data: twin } = useTwin()

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-black text-white font-sans selection:bg-white/20">
      <Header />
      <div className="flex-1 flex min-h-0">
        <SidebarNav />
        <main className="flex-1 flex flex-col min-h-0 bg-[#050505]">
          <section className="flex-1 flex relative">
            <div className="flex-1 relative bg-[#050505]">
              <PolyhouseScene onSelectZone={setSelectedZone} />
              <div className="absolute top-4 left-4 z-10 pointer-events-none">
                <h2 className="text-sm font-mono tracking-widest text-white/50 uppercase">3D Digital Twin</h2>
              </div>
            </div>

            <div className="w-80 border-l border-white/10 bg-[#0a0a0a] overflow-y-auto flex flex-col">
              <div className="p-4 border-b border-white/10 flex justify-between items-center">
                <h2 className="text-xs font-mono tracking-widest text-white/50 uppercase">Selected Zone</h2>
                <ProvenanceChip label="SIMULATED" />
              </div>
              
              <div className="p-4 flex-1">
                {!selectedZone ? (
                  <div className="h-full flex items-center justify-center text-[10px] font-mono text-white/30 uppercase text-center tracking-widest">
                    Click a zone in the 3D model<br/>to view details
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-mono text-xl font-bold">{selectedZone.toUpperCase()}</h3>
                      <p className="font-mono text-xs text-emerald-400 mt-1">
                        {twin?.zones.find(z => z.zone_id === selectedZone)?.crop_id?.replace("_", " ").toUpperCase() || "NO CROP"}
                      </p>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-[10px] text-white/40 font-mono uppercase">Temperature</div>
                        <div className="font-mono">{twin?.temperature_c.toFixed(1) ?? "--"} °C</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-white/40 font-mono uppercase">Humidity</div>
                        <div className="font-mono">{twin?.humidity_percent.toFixed(1) ?? "--"} %</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-white/40 font-mono uppercase">Moisture</div>
                        <div className="font-mono">{twin?.substrate_moisture_percent.toFixed(1) ?? "--"} %</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-white/40 font-mono uppercase">Stress</div>
                        <div className="font-mono">{twin?.crop_stress_index.toFixed(2) ?? "--"}</div>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-white/10">
                      <div className="text-[10px] text-white/40 font-mono uppercase mb-2">Infrastructure</div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-mono text-xs">Water Tank</span>
                        <span className="font-mono text-xs">{twin?.tank_volume_l.toFixed(0) ?? "--"} L</span>
                      </div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-mono text-xs">Pump Status</span>
                        <span className={`font-mono text-xs ${twin?.pump_state === "ON" ? "text-emerald-400" : "text-white/50"}`}>
                          {twin?.pump_state ?? "--"}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="font-mono text-xs">Sensor Health</span>
                        <span className={`font-mono text-xs ${twin?.sensor_health === "HEALTHY" ? "text-emerald-400" : "text-red-400"}`}>
                          {twin?.sensor_health ?? "--"}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  )
}
