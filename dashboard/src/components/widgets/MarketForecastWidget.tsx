"use client"

import { DashboardSnapshot } from "@/lib/api/types"
import { Droplet, ArrowDownToLine, ArrowUpFromLine, AlertCircle } from "lucide-react"

export function ResourceOptimizationWidget({ snapshot }: { snapshot: DashboardSnapshot | null }) {
  if (!snapshot) return null;

  const res = snapshot.resources;

  return (
    <div className="w-full h-full flex flex-col bg-[#121212]">
      <div className="px-4 py-3 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-sm text-white/90">Resource Optimization</h3>
      </div>
      <div className="flex-1 p-4 grid grid-cols-2 gap-4">
        <div className="bg-white/[0.02] border border-white/5 p-4 rounded-xl flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-2">
            <ArrowUpFromLine className="w-4 h-4 text-blue-500" />
            <span className="text-xs text-white/50">Requested Water</span>
          </div>
          <span className="text-xl font-medium text-white">{res.requested_water_l.toFixed(1)} L</span>
        </div>
        <div className="bg-white/[0.02] border border-white/5 p-4 rounded-xl flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-2">
            <ArrowDownToLine className="w-4 h-4 text-emerald-500" />
            <span className="text-xs text-white/50">Delivered Water</span>
          </div>
          <span className="text-xl font-medium text-white">{res.delivered_water_l.toFixed(1)} L</span>
        </div>
        <div className="bg-white/[0.02] border border-white/5 p-4 rounded-xl flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-4 h-4 text-orange-500" />
            <span className="text-xs text-white/50">Unmet Demand</span>
          </div>
          <span className={`text-xl font-medium ${res.unmet_water_demand_l > 0 ? "text-orange-500" : "text-white"}`}>
            {res.unmet_water_demand_l.toFixed(1)} L
          </span>
        </div>
        <div className="bg-white/[0.02] border border-white/5 p-4 rounded-xl flex flex-col justify-center">
          <div className="flex items-center gap-2 mb-2">
            <Droplet className="w-4 h-4 text-blue-400" />
            <span className="text-xs text-white/50">Remaining Reserve</span>
          </div>
          <span className="text-xl font-medium text-white">{res.remaining_water_l.toFixed(1)} L</span>
        </div>
      </div>
    </div>
  )
}

