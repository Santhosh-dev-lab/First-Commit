"use client"

import { useTelemetry } from "@/lib/api/client"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { useEffect, useState } from "react"
import { TelemetryResponse } from "@/lib/api/types"

// Keep last 20 data points for visualization
const MAX_HISTORY = 20

export function TelemetryCharts() {
  const { data: telemetry, error } = useTelemetry()
  const [history, setHistory] = useState<Record<string, any[]>>({})

  useEffect(() => {
    if (!telemetry) return

    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    
    setHistory(prev => {
      const next = { ...prev }
      telemetry.forEach(t => {
        const type = t.measurement_type
        if (!next[type]) next[type] = []
        next[type] = [...next[type], {
          time: now,
          value: t.value,
          zone: t.zone_id
        }].slice(-MAX_HISTORY)
      })
      return next
    })
  }, [telemetry])

  if (error) return <div className="text-red-500 font-mono text-xs">Failed to load telemetry</div>
  
  const hasHistory = Object.keys(history).some(k => history[k].length > 1)
  
  if (!hasHistory) {
    return (
      <div className="h-full flex items-center justify-center">
        <span className="text-xs font-mono text-white/30 tracking-widest uppercase">Waiting for telemetry...</span>
      </div>
    )
  }

  const getConfig = (type: string) => {
    switch(type) {
      case "substrate_moisture": return { icon: "💧", color: "#3b82f6", label: "Substrate Moisture", unit: "%" }
      case "temperature": return { icon: "🌡️", color: "#ef4444", label: "Temperature", unit: "°C" }
      case "humidity": return { icon: "💨", color: "#0ea5e9", label: "Humidity", unit: "%" }
      case "tank_volume": return { icon: "🛢️", color: "#3b82f6", label: "Water Tank", unit: "L" }
      case "crop_stress": return { icon: "🌱", color: "#22c55e", label: "Crop Stress", unit: "" }
      default: return { icon: "📊", color: "#10b981", label: type.replace("_", " "), unit: "" }
    }
  }

  return (
    <div className="flex h-full gap-4 pb-2">
      {Object.entries(history).map(([type, data]) => {
        const config = getConfig(type)
        const currentVal = data[data.length - 1]?.value
        
        return (
          <div key={type} className="flex-1 flex flex-col border border-white/10 bg-[#080808] p-4">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="text-[10px] font-mono text-white/40 uppercase tracking-widest flex items-center gap-2">
                  <span>{config.icon}</span>
                  {config.label}
                </div>
                <div className="text-xl font-mono font-bold text-white mt-1">
                  {currentVal?.toLocaleString(undefined, { maximumFractionDigits: 1 })} <span className="text-xs text-white/30">{config.unit}</span>
                </div>
              </div>
              <div className="text-[9px] font-mono text-emerald-500 border border-emerald-500/20 px-1 bg-emerald-500/5">LIVE</div>
            </div>
            
            <div className="flex-1 min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 5, right: 0, bottom: 0, left: -20 }}>
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke={config.color} 
                    strokeWidth={1}
                    dot={false}
                    isAnimationActive={false}
                  />
                  <XAxis 
                    dataKey="time" 
                    stroke="#ffffff20" 
                    fontSize={8} 
                    tickMargin={4}
                    tickFormatter={(val, i) => i % 3 === 0 ? val : ''}
                    axisLine={false}
                  />
                  <YAxis 
                    stroke="#ffffff20" 
                    fontSize={8}
                    domain={['auto', 'auto']} 
                    tickCount={5}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#000', border: '1px solid #333', borderRadius: '4px', padding: '4px' }}
                    itemStyle={{ color: config.color, fontSize: '10px', fontFamily: 'monospace' }}
                    labelStyle={{ color: '#888', fontSize: '8px', fontFamily: 'monospace', display: 'none' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )
      })}
    </div>
  )
}
