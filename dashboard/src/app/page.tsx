"use client"

import { Header } from "@/components/dashboard/Header"
import { SidebarNav } from "@/components/dashboard/SidebarNav"
import { KPIHeader } from "@/components/overview/KPIHeader"
import { FieldMap } from "@/components/overview/FieldMap"
import { ZoneHealthTable } from "@/components/operations/ZoneHealthTable"
import { IrrigationDonut } from "@/components/overview/IrrigationDonut"
import { AlertsWidget } from "@/components/widgets/AlertsWidget"
import { AdvisoryWidget } from "@/components/widgets/AdvisoryWidget"
import { PestDiseaseWidget } from "@/components/widgets/PestDiseaseWidget"
import { MarketForecastWidget } from "@/components/widgets/MarketForecastWidget"
import { useTwin, useHealth } from "@/lib/api/client"
import { Activity, Radio, Box, ShieldCheck, Cpu } from "lucide-react"

export default function Dashboard() {
  const { data: twin } = useTwin()
  const { data: health } = useHealth()
  const isOnline = !!twin

  return (
    <div className="h-screen w-full flex overflow-hidden bg-[#050505] text-white font-sans selection:bg-white/20">
      <SidebarNav />
      
      <div className="flex-1 flex flex-col min-w-0 h-full">
        <Header />
        
        <main className="flex-1 overflow-y-auto bg-[#050505] p-6 space-y-6">
          <KPIHeader twin={twin} />
          
          {/* Row 2: Field Map, Soil Health, Irrigation */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
            <div className="bg-[#121212] border border-white/5 rounded-xl flex flex-col overflow-hidden">
               <FieldMap twin={twin} />
            </div>
            
            <div className="bg-[#121212] border border-white/5 rounded-xl flex flex-col overflow-hidden">
               <ZoneHealthTable twin={twin} />
            </div>

            <div className="bg-[#121212] border border-white/5 rounded-xl flex flex-col overflow-hidden">
               <IrrigationDonut twin={twin} />
            </div>
          </div>

          {/* Row 3: Alerts, Advisory, Pest, Market */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
            <div className="bg-[#121212] border border-white/5 rounded-xl flex flex-col overflow-hidden">
               <AlertsWidget />
            </div>

            <div className="bg-[#121212] border border-white/5 rounded-xl flex flex-col overflow-hidden">
               <AdvisoryWidget />
            </div>

            <div className="bg-[#121212] border border-white/5 rounded-xl flex flex-col overflow-hidden">
               <PestDiseaseWidget />
            </div>
            
            <div className="bg-[#121212] border border-white/5 rounded-xl flex flex-col overflow-hidden">
               <MarketForecastWidget />
            </div>
          </div>

          {/* Bottom Footer */}
          <footer className="mt-8 border-t border-white/10 pt-4 pb-2 flex items-center justify-between text-[11px] font-sans text-white/50">
             <div className="flex items-center gap-2">
               <Activity className="w-3.5 h-3.5" />
               <span>Last Data Sync: {isOnline ? new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : 'N/A'}</span>
             </div>
             
             <div className="flex items-center gap-8">
               <div className="flex items-center gap-2">
                 <Radio className="w-3.5 h-3.5 text-emerald-500" />
                 <span>Gateway Status: <span className="text-emerald-500">Online</span></span>
               </div>
               
               <div className="flex items-center gap-2">
                 <Box className="w-3.5 h-3.5 text-emerald-500" />
                 <span>Active Nodes: <span className="text-emerald-500">12/12</span></span>
               </div>

               <div className="flex items-center gap-2">
                 <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                 <span>Battery Health (Avg): <span className="text-emerald-500">87%</span></span>
               </div>
             </div>
             
             <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                <span>Data Source: <span className="text-white/80">Live</span></span>
             </div>
          </footer>
        </main>
      </div>
    </div>
  )
}
