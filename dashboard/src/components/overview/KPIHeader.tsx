"use client"

import { Droplet, Activity, Zap, CheckCircle2, CloudRain, Flame, Bug, Target } from "lucide-react"

interface KPIHeaderProps {
  twin: any
}

export function KPIHeader({ twin }: KPIHeaderProps) {
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
            <p className="text-xl font-medium text-white mt-0.5">6 <span className="text-sm text-white/50 font-normal">of 6</span></p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
          All zones online
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
            <p className="text-xl font-medium text-white mt-0.5">28%</p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
          Optimal Range: 20–40%
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
            <p className="text-xl font-medium text-emerald-500 mt-0.5">ON</p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
          Next Cycle: 6:00 PM
        </div>
      </div>

      {/* 4. Rainfall Forecast */}
      <div className="p-4 bg-[#121212] border border-white/5 rounded-xl flex flex-col justify-between h-28 relative overflow-hidden">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-500/10 rounded-full shrink-0 mt-1">
            <CloudRain className="w-5 h-5 text-blue-500" />
          </div>
          <div>
            <h3 className="text-[11px] font-medium text-white/70">Rainfall Forecast</h3>
            <p className="text-xl font-medium text-white mt-0.5">12 <span className="text-sm text-white/50 font-normal">mm</span></p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
          In next 48 hours
        </div>
      </div>

      {/* 5. Fire Risk */}
      <div className="p-4 bg-[#121212] border border-white/5 rounded-xl flex flex-col justify-between h-28 relative overflow-hidden">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-red-500/10 rounded-full shrink-0 mt-1">
            <Flame className="w-5 h-5 text-red-500" />
          </div>
          <div>
            <h3 className="text-[11px] font-medium text-white/70">Fire Risk</h3>
            <p className="text-xl font-medium text-emerald-500 mt-0.5">Low</p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60">
          <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
          Risk Score: 12/100
        </div>
      </div>

      {/* 6. Pest Risk */}
      <div className="p-4 bg-[#121212] border border-white/5 rounded-xl flex flex-col justify-between h-28 relative overflow-hidden">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-yellow-500/10 rounded-full shrink-0 mt-1">
            <Bug className="w-5 h-5 text-yellow-500" />
          </div>
          <div>
            <h3 className="text-[11px] font-medium text-white/70">Pest Risk</h3>
            <p className="text-xl font-medium text-yellow-500 mt-0.5">Moderate</p>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-1.5 text-[10px] text-white/60 text-yellow-500">
          Monitor Closely
        </div>
      </div>

    </div>
  )
}
