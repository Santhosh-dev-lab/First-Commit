"use client"

import { useHealth } from "@/lib/api/client"
import { cn } from "@/lib/utils"
import { useEffect, useState } from "react"
import { ShieldCheck, Activity, Cpu, Box, CloudSun } from "lucide-react"

function StatusIndicator({ label, status, icon: Icon, healthy = true }: { label: string, status: string, icon: any, healthy?: boolean }) {
  return (
    <div className="flex flex-col items-center px-4">
      <div className="flex items-center gap-2 mb-1">
        <Icon className={cn("w-4 h-4", healthy ? "text-emerald-400" : "text-amber-400")} />
        <span className="text-[10px] font-mono text-white/50 tracking-widest uppercase">{label}</span>
      </div>
      <span className={cn("text-xs font-bold tracking-widest uppercase", healthy ? "text-emerald-400" : "text-amber-400")}>
        {status}
      </span>
    </div>
  )
}

export function Header() {
  const { data: health, error } = useHealth()
  const isHealthy = !error && health?.status === "healthy"
  const isConnected = !!health
  
  const [time, setTime] = useState<Date | null>(null)
  
  useEffect(() => {
    setTime(new Date())
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <header className="h-16 border-b border-white/5 bg-[#0a0a0a] flex items-center justify-between px-6 shrink-0 z-50">
      <div className="flex flex-col justify-center">
        <h1 className="text-xl font-light tracking-[0.2em] text-white">PHYSICA</h1>
        <p className="text-[9px] text-white/40 font-mono tracking-widest uppercase mt-0.5">A Compiler for Physical Reality</p>
      </div>
      
      <div className="flex items-center divide-x divide-white/5">
        <StatusIndicator 
          label="System" 
          status={isConnected ? "ONLINE" : "OFFLINE"} 
          icon={Activity}
          healthy={isConnected} 
        />
        <StatusIndicator 
          label="Physical Mode" 
          status="SIMULATION" 
          icon={CloudSun}
          healthy={true} 
        />
        <StatusIndicator 
          label="Agent" 
          status={health?.agent_provider || "MOCK"} 
          icon={Cpu}
          healthy={true} 
        />
        <StatusIndicator 
          label="Digital Twin" 
          status={isConnected ? "SYNCHRONIZED" : "STALE"} 
          icon={Box}
          healthy={isConnected} 
        />
        <StatusIndicator 
          label="Safety" 
          status={health?.safety || "ARMED"} 
          icon={ShieldCheck}
          healthy={isHealthy} 
        />
        
        <div className="flex flex-col items-end px-4 min-w-[120px]">
          <span className="text-[10px] font-mono text-white/50 uppercase">
            {time ? time.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : "---"}
          </span>
          <span className="text-sm font-mono text-white font-bold tracking-widest">
            {time ? time.toLocaleTimeString('en-US', { hour12: false }) : "--:--:--"}
          </span>
        </div>
      </div>
    </header>
  )
}
