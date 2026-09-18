"use client"

import { DashboardSnapshot, AlertSummary } from "@/lib/api/types"
import { AlertCircle, AlertTriangle, Info } from "lucide-react"

export function AlertsWidget({ snapshot }: { snapshot: DashboardSnapshot | null }) {
  if (!snapshot) return null;

  const alerts = snapshot.alerts || [];

  return (
    <div className="w-full h-full flex flex-col bg-[#121212]">
      <div className="px-4 py-3 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-sm text-white/90">Alerts & Notifications</h3>
        <span className="text-xs text-blue-400 cursor-pointer hover:underline">View All</span>
      </div>
      <div className="flex-1 p-0 overflow-auto">
        {alerts.length === 0 ? (
          <div className="flex items-center justify-center h-full text-white/50 text-sm py-8">
            NO ACTIVE ALERTS
          </div>
        ) : (
          <ul className="divide-y divide-white/5">
            {alerts.map((alert: AlertSummary) => (
              <li key={alert.id} className="p-4 hover:bg-white/[0.02] flex items-start gap-3">
                {alert.severity === "CRITICAL" ? (
                  <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                ) : alert.severity === "WARNING" ? (
                  <AlertTriangle className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />
                ) : (
                  <Info className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white/90 font-medium truncate">{alert.message}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-white/50">{alert.category}</span>
                    {alert.zone_id && (
                      <span className="text-xs text-white/50 bg-white/5 px-1.5 py-0.5 rounded">
                        {alert.zone_id}
                      </span>
                    )}
                  </div>
                </div>
                <span className="text-xs text-white/40 whitespace-nowrap">
                  {new Date(alert.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

