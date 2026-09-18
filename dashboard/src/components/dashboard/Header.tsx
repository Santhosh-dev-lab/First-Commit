"use client"

import { useHealth, useDashboard } from "@/lib/api/client"
import { useEffect, useState } from "react"
import { Bell, Calendar, ChevronDown, Globe } from "lucide-react"

export function Header() {
  const { data: snapshot } = useDashboard()
  const { data: health, error } = useHealth()
  const isHealthy = !error && health?.status === "healthy"
  
  const [time, setTime] = useState<Date | null>(null)
  
  useEffect(() => {
    setTime(new Date())
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <header className="h-20 border-b border-white/5 bg-[#0a0a0a] flex items-center justify-between px-6 shrink-0 z-50">
      <div className="flex flex-col justify-center">
        <h1 className="text-xl font-medium text-white flex items-center gap-2">
          Good morning! <span className="text-emerald-400">🌱</span>
        </h1>
        <p className="text-[13px] text-white/50 mt-1">Here's what's happening in your farm today.</p>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Status Pill */}
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-white/80">
          <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></div>
          All Systems Operational
        </div>
        
        {/* Language Selector */}
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-white/80 cursor-pointer hover:bg-white/10 transition-colors">
          <Globe className="w-4 h-4 text-white/60" />
          English
          <ChevronDown className="w-3 h-3 text-white/50" />
        </div>

        {/* Notification Bell */}
        <button className="w-9 h-9 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/80 hover:bg-white/10 transition-colors relative">
          <Bell className="w-4 h-4" />
          <div className="absolute top-2 right-2 w-1.5 h-1.5 bg-red-500 rounded-full border border-[#0a0a0a]"></div>
        </button>

        {/* Date Time */}
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-white/80">
          <Calendar className="w-4 h-4 text-white/60" />
          {time ? (
            <>
              {time.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}, {time.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
            </>
          ) : (
            "Loading..."
          )}
        </div>
      </div>
    </header>
  )
}

