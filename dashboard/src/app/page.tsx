"use client"

import { Header } from "@/components/dashboard/Header"
import { SidebarNav } from "@/components/dashboard/SidebarNav"
import { KPIHeader } from "@/components/overview/KPIHeader"
import { SiteSchematic2D } from "@/components/overview/SiteSchematic2D"
import { SystemHealth } from "@/components/system/SystemHealth"
import { useTwin } from "@/lib/api/client"

export default function Dashboard() {
  const { data: twin } = useTwin()

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-black text-white font-sans selection:bg-white/20">
      <Header />
      
      <div className="flex-1 flex min-h-0">
        <SidebarNav />
        
        <main className="flex-1 flex flex-col min-h-0 bg-[#050505] overflow-y-auto p-6 space-y-6">
          <KPIHeader twin={twin} />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-[#0a0a0a] border border-white/10 rounded-lg p-6">
              <h2 className="text-xs font-mono tracking-widest text-white/50 uppercase mb-4">Polyhouse Overview</h2>
              <SiteSchematic2D twin={twin} />
            </div>
            
            <div className="bg-[#0a0a0a] border border-white/10 rounded-lg p-6 flex flex-col">
              <h2 className="text-xs font-mono tracking-widest text-white/50 uppercase mb-4">System Health</h2>
              <SystemHealth />
            </div>
          </div>
          
        </main>
      </div>
    </div>
  )
}
