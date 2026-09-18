"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Home, LayoutDashboard, Activity, Droplets, Cpu, Settings2, GitBranch, Server, Box } from "lucide-react"

export function SidebarNav() {
  const pathname = usePathname()

  const links = [
    { name: "Overview", href: "/", icon: Home },
    { name: "Operations", href: "/operations", icon: LayoutDashboard },
    { name: "Telemetry", href: "/telemetry", icon: Activity },
    { name: "Resources", href: "/resources", icon: Droplets },
    { name: "AI / Agents", href: "/agents", icon: Cpu },
    { name: "Control Center", href: "/control", icon: Settings2 },
    { name: "Scenarios", href: "/scenarios", icon: GitBranch },
    { name: "System", href: "/system", icon: Server },
    { name: "Digital Twin", href: "/twin", icon: Box },
  ]

  return (
    <aside className="w-56 border-r border-white/10 bg-[#050505] flex flex-col pt-4">
      <nav className="flex flex-col gap-0.5 px-3">
        {links.map((link) => {
          const isActive = pathname === link.href
          return (
            <Link 
              key={link.name}
              href={link.href} 
              className={`flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors ${
                isActive 
                  ? "bg-white/10 text-white border-l-2 border-emerald-500 rounded-r" 
                  : "text-white/50 hover:text-white hover:bg-white/5 rounded border-l-2 border-transparent"
              }`}
            >
              <link.icon className={`w-4 h-4 ${isActive ? "text-emerald-400" : ""}`} />
              {link.name}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
