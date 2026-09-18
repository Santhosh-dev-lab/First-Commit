"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { 
  Home, 
  Map, 
  LineChart, 
  Sprout, 
  Droplets, 
  Bell, 
  Bug, 
  CloudSun, 
  TrendingUp, 
  Landmark, 
  FileText, 
  Server, 
  Settings,
  ChevronDown
} from "lucide-react"

export function SidebarNav() {
  const pathname = usePathname()

  const links = [
    { name: "Overview", href: "/", icon: Home },
    { name: "Field Map", href: "/field-map", icon: Map },
    { name: "Soil Analytics", href: "/soil", icon: LineChart },
    { name: "Crop Advisory", href: "/advisory", icon: Sprout },
    { name: "Irrigation Control", href: "/irrigation", icon: Droplets },
    { name: "Alerts", href: "/alerts", icon: Bell, badge: 3 },
    { name: "Pest & Disease", href: "/pest", icon: Bug },
    { name: "Weather", href: "/weather", icon: CloudSun },
    { name: "Market Prices", href: "/market", icon: TrendingUp },
    { name: "Government Schemes", href: "/schemes", icon: Landmark },
    { name: "Reports", href: "/reports", icon: FileText },
    { name: "Devices", href: "/devices", icon: Server },
    { name: "Settings", href: "/settings", icon: Settings },
  ]

  return (
    <aside className="w-[260px] shrink-0 border-r border-white/10 bg-[#0a0a0a] flex flex-col h-full z-50 overflow-hidden">
      
      {/* Brand */}
      <div className="flex flex-col justify-center px-6 py-6 mb-2">
        <h1 className="text-2xl font-bold tracking-tight text-emerald-500">
          Sasya<span className="text-emerald-400">Logix</span>
        </h1>
        <p className="text-xs text-white/50 tracking-wider mt-0.5">Intelligence Hub</p>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 flex flex-col gap-1 px-4 overflow-y-auto overflow-x-hidden scrollbar-hide">
        {links.map((link) => {
          const isActive = pathname === link.href
          return (
            <Link 
              key={link.name}
              href={link.href} 
              className={`flex items-center justify-between px-4 py-2.5 text-[13px] font-medium transition-colors ${
                isActive 
                  ? "bg-emerald-500/10 text-white border-l-2 border-emerald-500 rounded-r" 
                  : "text-white/60 hover:text-white hover:bg-white/5 rounded border-l-2 border-transparent"
              }`}
            >
              <div className="flex items-center gap-3">
                <link.icon className={`w-4 h-4 ${isActive ? "text-emerald-500" : "text-white/40"}`} />
                {link.name}
              </div>
              {link.badge && (
                <span className="flex items-center justify-center w-4 h-4 text-[10px] font-bold text-white bg-red-500 rounded-full">
                  {link.badge}
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Bottom Profile / Weather Widget */}
      <div className="p-4 border-t border-white/5 bg-black/20">
        
        {/* Profile Card */}
        <div className="flex items-center gap-3 p-2 bg-white/5 rounded-lg border border-white/5 mb-4">
          <div className="w-10 h-10 rounded-full bg-emerald-900 overflow-hidden border border-emerald-500/30 flex shrink-0 items-center justify-center">
             <Sprout className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="flex-1 overflow-hidden">
            <h4 className="text-sm font-semibold text-white truncate">Ramesh Farm</h4>
            <p className="text-[10px] text-white/50">Farm ID: FARM1234</p>
            <p className="text-[10px] text-white/50">Area: 24.8 ha</p>
          </div>
          <div className="px-1 text-white/40">
             <ChevronDown className="w-4 h-4" />
          </div>
        </div>

        {/* Weather Brief */}
        <div className="px-2">
          <div className="flex items-center gap-3 mb-3">
            <CloudSun className="w-8 h-8 text-yellow-400" />
            <div>
              <div className="text-xl font-light text-white">24°C</div>
              <div className="text-xs text-white/50">Partly Cloudy</div>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-2 text-center text-white/80 mb-3 border-b border-white/5 pb-3">
            <div>
              <div className="text-xs font-medium">12 km/h</div>
              <div className="text-[10px] text-white/40">Wind</div>
            </div>
            <div>
              <div className="text-xs font-medium">0 mm</div>
              <div className="text-[10px] text-white/40">Rain (24h)</div>
            </div>
            <div>
              <div className="text-xs font-medium">68%</div>
              <div className="text-[10px] text-white/40">Humidity</div>
            </div>
          </div>
          
          <div className="flex justify-between items-center text-[10px] text-white/40">
            <span>Rajapur, Maharashtra</span>
            <span>Today, 10:30 AM</span>
          </div>
        </div>

      </div>
    </aside>
  )
}
