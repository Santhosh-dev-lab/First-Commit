"use client"

import { DashboardSnapshot } from "@/lib/api/types"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"

export function IrrigationDonut({ snapshot }: { snapshot: DashboardSnapshot | null }) {
  if (!snapshot) {
    return <div className="w-full h-full bg-[#121212] flex items-center justify-center text-white/50 text-sm">WAITING FOR DATA</div>
  }

  const activeCount = snapshot.zones.filter(z => z.irrigation_status === "ON").length;
  const idleCount = snapshot.zones.length - activeCount;

  const data = [
    { name: "Active", value: activeCount, color: "#10b981" }, // emerald-500
    { name: "Idle", value: idleCount, color: "#3f3f46" },    // zinc-700
  ];

  return (
    <div className="w-full h-full flex flex-col bg-[#121212]">
      <div className="px-4 py-3 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-sm text-white/90">Irrigation Status</h3>
      </div>
      <div className="flex-1 p-4 relative min-h-[250px] flex items-center justify-center">
        {snapshot.zones.length === 0 ? (
          <div className="text-white/30 text-sm">NO ZONES CONFIGURED</div>
        ) : (
          <>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: "#1a1a1a", borderColor: "rgba(255,255,255,0.1)", color: "#fff" }}
                  itemStyle={{ color: "#fff" }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-3xl font-bold text-white">{snapshot.zones.length}</span>
              <span className="text-[10px] text-white/50 uppercase">Zones</span>
            </div>
          </>
        )}
      </div>
      
      {snapshot.zones.length > 0 && (
        <div className="px-6 pb-4 flex justify-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
            <span className="text-xs text-white/70">{activeCount} Active</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-zinc-700"></div>
            <span className="text-xs text-white/70">{idleCount} Idle</span>
          </div>
        </div>
      )}
    </div>
  )
}

