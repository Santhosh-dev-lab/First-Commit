"use client"

import { useEffect, useState } from "react"
import { Activity, Server, Radio, RefreshCw } from "lucide-react"

import { Card } from "@/components/ui/Card"

export default function ConnectivityPage() {
  const [connectivity, setConnectivity] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const fetchConnectivity = async () => {
    setLoading(true)
    try {
      const res = await fetch("/api/settings/connectivity")
      const data = await res.json()
      setConnectivity(data)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchConnectivity()
  }, [])

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-light text-white tracking-tight">Farm Connectivity</h1>
          <p className="text-white/50 mt-1">Manage physical hardware and simulation modes.</p>
        </div>
        <button 
          onClick={fetchConnectivity}
          className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-white/70 transition-colors"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-white/5 border-white/10 p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-medium text-white">Current Mode</h2>
              <p className="text-sm text-white/50">Data ingestion source</p>
            </div>
          </div>
          
          <div className="bg-black/20 p-4 rounded-lg border border-white/5 mt-4">
            <div className="text-2xl font-light text-white mb-1">
              {connectivity?.mode?.replace("_", " ") || "UNKNOWN"}
            </div>
            <div className="text-xs text-emerald-400">Active and routing telemetry</div>
          </div>
        </Card>

        <Card className="bg-white/5 border-white/10 p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-blue-500/10 text-blue-400 rounded-xl">
              <Radio className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-medium text-white">Gateway Status</h2>
              <p className="text-sm text-white/50">Edge synchronization</p>
            </div>
          </div>
          
          <div className="bg-black/20 p-4 rounded-lg border border-white/5 mt-4">
            <div className="flex justify-between items-end">
              <div>
                <div className="text-2xl font-light text-white mb-1">
                  {connectivity?.status || "UNKNOWN"}
                </div>
                <div className="text-xs text-white/40">
                  ID: {connectivity?.gateway_id || "None"}
                </div>
              </div>
              <div className={`w-3 h-3 rounded-full ${connectivity?.status === 'CONNECTED' ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'bg-red-500'}`} />
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
