"use client"

import { useEffect, useState } from "react"
import { Server, Activity, Plus } from "lucide-react"

import { Card } from "@/components/ui/card"

export default function DevicesPage() {
  const [devices, setDevices] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchDevices = async () => {
    setLoading(true)
    try {
      const res = await fetch("/api/devices")
      const data = await res.json()
      setDevices(Array.isArray(data) ? data : [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchDevices()
  }, [])

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-light text-white tracking-tight">Devices</h1>
          <p className="text-white/50 mt-1">Manage edge gateways, sensors, and actuators.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors font-medium">
          <Plus className="w-4 h-4" />
          Pair Gateway
        </button>
      </div>

      <div className="space-y-4">
        {loading ? (
          <div className="text-white/50 text-center py-12">Loading devices...</div>
        ) : devices.length === 0 ? (
          <div className="text-white/50 text-center py-12 bg-white/5 rounded-xl border border-white/10">
            No devices found. Pair a gateway to discover devices.
          </div>
        ) : (
          devices.map(device => (
            <Card key={device.id} className="bg-white/5 border-white/10 p-4 flex items-center justify-between hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-black/30 text-white/70 rounded-xl">
                  {device.device_type === "gateway" ? <Server className="w-5 h-5" /> : <Activity className="w-5 h-5" />}
                </div>
                <div>
                  <h3 className="text-white font-medium">{device.name}</h3>
                  <p className="text-xs text-white/50">{device.id} • {device.device_type.toUpperCase()}</p>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-sm font-medium ${device.status === 'ONLINE' ? 'text-emerald-400' : 'text-white/40'}`}>
                  {device.status}
                </div>
                <div className="text-xs text-white/30">
                  Zone: {device.zone_id || "Unassigned"}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
