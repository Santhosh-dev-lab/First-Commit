"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { CheckCircle2, ChevronRight, Server, Cloud, Cpu } from "lucide-react"

type StepConfig = {
  id: string
  title: string
}

const STEPS: StepConfig[] = [
  { id: "welcome", title: "WELCOME" },
  { id: "farm", title: "FARM" },
  { id: "environment", title: "ENVIRONMENT" },
  { id: "zones", title: "ZONES" },
  { id: "crops", title: "CROPS" },
  { id: "resources", title: "RESOURCES" },
  { id: "devices", title: "DEVICES" },
  { id: "connection", title: "CONNECTION" },
  { id: "review", title: "REVIEW" }
]

export default function Onboarding() {
  const router = useRouter()
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  // Form states
  const [farmData, setFarmData] = useState({ name: "", location: "" })
  const [envData, setEnvData] = useState({ type: "Polyhouse", area_sqm: 1000 })
  const [zones, setZones] = useState([{ id: 1, name: "Zone 1", area_sqm: 500, crop_id: "dwarf_tomato", growth_stage: "Vegetative" }])
  const [resources, setResources] = useState({ tank_capacity_l: 5000, energy_source: "Grid" })
  const [devices, setDevices] = useState([{ name: "Main Pump", type: "Pump" }])
  const [connectionMode, setConnectionMode] = useState("LOCAL_SIMULATION")
  const [availableCrops, setAvailableCrops] = useState<{crop_id: string, name: string}[]>([])

  useEffect(() => {
    // Fetch initial status
    fetch("/api/onboarding/status")
      .then(res => res.json())
      .then(data => {
        if (data.completed) {
          router.push("/app/overview")
        } else {
          setCurrentStepIndex(Math.max(0, data.current_step - 1))
          setLoading(false)
        }
      })
      .catch(() => setLoading(false))

    // Fetch crops
    fetch("/api/crops")
      .then(res => res.json())
      .then(data => {
        setAvailableCrops(data)
      })
      .catch(console.error)
  }, [router])

  const saveFarm = async () => {
    await fetch("/api/onboarding/farm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(farmData)
    })
  }

  const saveEnv = async () => {
    await fetch("/api/onboarding/environment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(envData)
    })
  }

  const saveZonesAndCrops = async () => {
    await fetch("/api/onboarding/zones", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(zones)
    })
  }

  const saveResources = async () => {
    await fetch("/api/onboarding/resources", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(resources)
    })
  }

  const saveDevices = async () => {
    await fetch("/api/onboarding/devices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(devices)
    })
  }

  const saveConnection = async () => {
    await fetch("/api/onboarding/connection", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: connectionMode })
    })
  }

  const handleNext = async () => {
    setSaving(true)
    try {
      const stepId = STEPS[currentStepIndex].id
      if (stepId === "farm") await saveFarm()
      else if (stepId === "environment") await saveEnv()
      else if (stepId === "crops") await saveZonesAndCrops()
      else if (stepId === "resources") await saveResources()
      else if (stepId === "devices") await saveDevices()
      else if (stepId === "connection") await saveConnection()
      else if (stepId === "review") {
        await fetch("/api/onboarding/complete", { method: "POST" })
        router.push("/app/overview")
        return
      }
      
      setCurrentStepIndex(prev => Math.min(prev + 1, STEPS.length - 1))
    } catch (e) {
      console.error(e)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center">Loading...</div>
  }

  const currentStep = STEPS[currentStepIndex]

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans flex flex-col">
      {/* Header / Progress */}
      <header className="border-b border-white/10 bg-[#0a0a0a] p-4 flex items-center justify-center overflow-x-auto">
        <div className="flex items-center gap-2 text-xs font-medium text-white/50 tracking-wider whitespace-nowrap px-4">
          {STEPS.map((step, idx) => (
            <div key={step.id} className="flex items-center gap-2">
              <span className={idx === currentStepIndex ? "text-emerald-400" : (idx < currentStepIndex ? "text-white" : "")}>
                {step.title}
              </span>
              {idx < STEPS.length - 1 && <ChevronRight className="w-3 h-3" />}
            </div>
          ))}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-2xl bg-[#121212] border border-white/10 rounded-xl p-8 shadow-2xl">
          
          {currentStep.id === "welcome" && (
            <div className="text-center space-y-4">
              <h1 className="text-3xl font-light">Welcome to PHYSICA</h1>
              <p className="text-white/60">Let's configure your physical environment so PHYSICA can understand your system. This establishes the physical context used by the deterministic core.</p>
            </div>
          )}

          {currentStep.id === "farm" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-light">Farm Details</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-1">Farm Name</label>
                  <input type="text" value={farmData.name} onChange={e => setFarmData({...farmData, name: e.target.value})} className="w-full bg-black border border-white/10 rounded p-2 text-white focus:outline-none focus:border-emerald-500/50" placeholder="e.g. My Research Polyhouse" />
                </div>
                <div>
                  <label className="block text-sm text-white/60 mb-1">Location (Optional)</label>
                  <input type="text" value={farmData.location} onChange={e => setFarmData({...farmData, location: e.target.value})} className="w-full bg-black border border-white/10 rounded p-2 text-white focus:outline-none focus:border-emerald-500/50" />
                </div>
              </div>
            </div>
          )}

          {currentStep.id === "environment" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-light">Environment</h2>
              <p className="text-white/60 text-sm">What physical environment are you managing?</p>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-1">Environment Type</label>
                  <select value={envData.type} onChange={e => setEnvData({...envData, type: e.target.value})} className="w-full bg-black border border-white/10 rounded p-2 text-white focus:outline-none focus:border-emerald-500/50">
                    <option>Polyhouse</option>
                    <option>Greenhouse</option>
                    <option>Indoor Farm</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-white/60 mb-1">Total Area (sqm)</label>
                  <input type="number" value={envData.area_sqm} onChange={e => setEnvData({...envData, area_sqm: Number(e.target.value)})} className="w-full bg-black border border-white/10 rounded p-2 text-white focus:outline-none focus:border-emerald-500/50" />
                </div>
              </div>
            </div>
          )}

          {currentStep.id === "zones" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-light">Zones</h2>
              <div className="space-y-4">
                {zones.map((zone, idx) => (
                  <div key={zone.id} className="p-4 border border-white/10 rounded-lg bg-black space-y-3">
                    <div className="flex justify-between items-center">
                      <h3 className="font-medium">Zone {idx + 1}</h3>
                      {zones.length > 1 && (
                        <button onClick={() => setZones(zones.filter(z => z.id !== zone.id))} className="text-red-400 text-sm hover:underline">Remove</button>
                      )}
                    </div>
                    <div>
                      <label className="block text-xs text-white/60 mb-1">Name</label>
                      <input type="text" value={zone.name} onChange={e => { const nz = [...zones]; nz[idx].name = e.target.value; setZones(nz) }} className="w-full bg-[#121212] border border-white/10 rounded p-1.5 text-sm focus:outline-none focus:border-emerald-500/50" />
                    </div>
                    <div>
                      <label className="block text-xs text-white/60 mb-1">Area (sqm)</label>
                      <input type="number" value={zone.area_sqm} onChange={e => { const nz = [...zones]; nz[idx].area_sqm = Number(e.target.value); setZones(nz) }} className="w-full bg-[#121212] border border-white/10 rounded p-1.5 text-sm focus:outline-none focus:border-emerald-500/50" />
                    </div>
                  </div>
                ))}
                <button onClick={() => setZones([...zones, { id: Date.now(), name: `Zone ${zones.length + 1}`, area_sqm: 100, crop_id: "dwarf_tomato", growth_stage: "Vegetative" }])} className="text-emerald-400 text-sm hover:underline">
                  + Add Zone
                </button>
              </div>
            </div>
          )}

          {currentStep.id === "crops" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-light">Crops</h2>
              <div className="space-y-4">
                {zones.map((zone, idx) => (
                  <div key={zone.id} className="p-4 border border-white/10 rounded-lg bg-black space-y-3">
                    <h3 className="font-medium text-emerald-400">{zone.name}</h3>
                    <div>
                      <label className="block text-xs text-white/60 mb-1">Crop Assignment</label>
                      <select value={zone.crop_id || ""} onChange={e => { const nz = [...zones]; nz[idx].crop_id = e.target.value; setZones(nz) }} className="w-full bg-[#121212] border border-white/10 rounded p-1.5 text-sm focus:outline-none focus:border-emerald-500/50">
                        {availableCrops.map(c => (
                          <option key={c.crop_id} value={c.crop_id}>{c.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentStep.id === "resources" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-light">Resources</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-1">Water Tank Capacity (L)</label>
                  <input type="number" value={resources.tank_capacity_l} onChange={e => setResources({...resources, tank_capacity_l: Number(e.target.value)})} className="w-full bg-black border border-white/10 rounded p-2 text-white focus:outline-none focus:border-emerald-500/50" />
                </div>
              </div>
            </div>
          )}

          {currentStep.id === "devices" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-light">Devices & Infrastructure</h2>
              <p className="text-white/60 text-sm">Define physical actuators and sensors. (Simulated for this demo)</p>
              <div className="space-y-4">
                {devices.map((device, idx) => (
                  <div key={idx} className="p-4 border border-white/10 rounded-lg bg-black space-y-3">
                    <div className="flex gap-4">
                      <div className="flex-1">
                        <label className="block text-xs text-white/60 mb-1">Name</label>
                        <input type="text" value={device.name} onChange={e => { const nd = [...devices]; nd[idx].name = e.target.value; setDevices(nd) }} className="w-full bg-[#121212] border border-white/10 rounded p-1.5 text-sm focus:outline-none focus:border-emerald-500/50" />
                      </div>
                      <div className="flex-1">
                        <label className="block text-xs text-white/60 mb-1">Type</label>
                        <input type="text" value={device.type} disabled className="w-full bg-[#121212] border border-white/5 text-white/50 rounded p-1.5 text-sm" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentStep.id === "connection" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-light">Connect Farm</h2>
              <p className="text-white/60 text-sm">How do you want to connect your farm? Your farm configuration can be created now. Live measurements will appear after a connection is established.</p>
              
              <div className="space-y-4">
                <button 
                  onClick={() => setConnectionMode("LOCAL_SIMULATION")}
                  className={`w-full flex items-start gap-4 p-4 rounded-lg border transition-all text-left ${connectionMode === "LOCAL_SIMULATION" ? "border-emerald-500 bg-emerald-500/5" : "border-white/10 bg-black hover:border-white/30"}`}
                >
                  <Cpu className={`w-6 h-6 mt-1 ${connectionMode === "LOCAL_SIMULATION" ? "text-emerald-400" : "text-white/50"}`} />
                  <div>
                    <h3 className="font-medium">Local Simulation</h3>
                    <p className="text-sm text-white/60 mt-1">For development and demo. Emulates telemetry using the PHYSICA Simulation Engine.</p>
                  </div>
                </button>

                <button 
                  onClick={() => setConnectionMode("EDGE_GATEWAY")}
                  className={`w-full flex items-start gap-4 p-4 rounded-lg border transition-all text-left ${connectionMode === "EDGE_GATEWAY" ? "border-emerald-500 bg-emerald-500/5" : "border-white/10 bg-black hover:border-white/30"}`}
                >
                  <Server className={`w-6 h-6 mt-1 ${connectionMode === "EDGE_GATEWAY" ? "text-emerald-400" : "text-white/50"}`} />
                  <div>
                    <h3 className="font-medium">PHYSICA Edge Gateway</h3>
                    <p className="text-sm text-white/60 mt-1">Connect an actual physical farm gateway to receive real-world hardware telemetry.</p>
                  </div>
                </button>

                <button 
                  onClick={() => setConnectionMode("CONNECT_LATER")}
                  className={`w-full flex items-start gap-4 p-4 rounded-lg border transition-all text-left ${connectionMode === "CONNECT_LATER" ? "border-emerald-500 bg-emerald-500/5" : "border-white/10 bg-black hover:border-white/30"}`}
                >
                  <Cloud className={`w-6 h-6 mt-1 ${connectionMode === "CONNECT_LATER" ? "text-emerald-400" : "text-white/50"}`} />
                  <div>
                    <h3 className="font-medium">Connect Later</h3>
                    <p className="text-sm text-white/60 mt-1">Finish setup without physical connectivity. Dashboard will show a disconnected state.</p>
                  </div>
                </button>
              </div>
            </div>
          )}

          {currentStep.id === "review" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-light">Review Configuration</h2>
              <div className="space-y-4 text-sm bg-black border border-white/10 rounded-lg p-6">
                <div><span className="text-white/50">Farm:</span> {farmData.name}</div>
                <div><span className="text-white/50">Environment:</span> {envData.type} ({envData.area_sqm} sqm)</div>
                <div><span className="text-white/50">Zones:</span> {zones.length} configured</div>
                <div><span className="text-white/50">Tank Capacity:</span> {resources.tank_capacity_l} L</div>
                <div><span className="text-white/50">Connection:</span> {connectionMode.replace("_", " ")}</div>
                
                <div className="pt-4 mt-4 border-t border-white/10 flex items-center gap-2 text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Human approval for actions is ENABLED by default.</span>
                </div>
                <div className="flex items-center gap-2 text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Safety boundaries are ENABLED and cannot be bypassed.</span>
                </div>
              </div>
            </div>
          )}

          {/* Footer Actions */}
          <div className="mt-8 flex justify-between items-center pt-6 border-t border-white/10">
            <button 
              onClick={() => setCurrentStepIndex(prev => Math.max(0, prev - 1))}
              disabled={currentStepIndex === 0 || saving}
              className="px-4 py-2 text-sm text-white/60 hover:text-white disabled:opacity-30 transition-colors"
            >
              Back
            </button>
            <button 
              onClick={handleNext}
              disabled={saving || (currentStep.id === "farm" && !farmData.name)}
              className="px-6 py-2 bg-white text-black font-medium text-sm rounded hover:bg-gray-200 disabled:opacity-50 transition-colors"
            >
              {saving ? "Saving..." : currentStepIndex === STEPS.length - 1 ? "Complete Setup" : "Continue"}
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
