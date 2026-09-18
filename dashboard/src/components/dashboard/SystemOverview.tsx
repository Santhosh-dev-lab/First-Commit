"use client"

import { useTwin, useResources } from "@/lib/api/client"
import { Card, CardContent } from "@/components/ui/Card"
import { ProvenanceChip } from "@/components/ui/ProvenanceChip"

function MetricCard({ 
  label, 
  value, 
  unit, 
  provenance = "OBSERVED" 
}: { 
  label: string, 
  value: string | number, 
  unit?: string,
  provenance?: "OBSERVED" | "SIMULATED" | "COMPUTED" | "CONFIGURED" | "ASSUMED" | "PREDICTED"
}) {
  return (
    <Card>
      <CardContent className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-white/50 uppercase tracking-widest">{label}</span>
          <ProvenanceChip label={provenance} />
        </div>
        <div className="flex items-baseline gap-1 mt-1">
          <span className="text-2xl font-mono">{value}</span>
          {unit && <span className="text-sm font-mono text-white/50">{unit}</span>}
        </div>
      </CardContent>
    </Card>
  )
}

export function SystemOverview() {
  const { data: twin, error: twinError } = useTwin()
  const { data: resources, error: resError } = useResources()

  if (twinError || resError) return <div className="text-red-500 font-mono text-xs">PHYSICA backend unavailable</div>
  if (!twin || !resources) return <div className="text-white/50 font-mono text-xs">Waiting for telemetry...</div>

  // Grab the first zone for high-level overview if exists
  const primaryZone = twin.zones?.[0]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
      <MetricCard label="Water Tank" value={resources.tank_volume_l.toFixed(1)} unit="L" provenance="OBSERVED" />
      <MetricCard label="Temperature" value={twin.temperature_c.toFixed(1)} unit="°C" provenance="SIMULATED" />
      <MetricCard label="Humidity" value={twin.humidity_percent.toFixed(1)} unit="%" provenance="SIMULATED" />
      <MetricCard label="Moisture" value={twin.substrate_moisture_percent.toFixed(1)} unit="%" provenance="SIMULATED" />
      <MetricCard label="Active Zone" value={primaryZone?.zone_id || "N/A"} provenance="CONFIGURED" />
      <MetricCard label="Active Crop" value={primaryZone?.crop_id || "N/A"} provenance="CONFIGURED" />
    </div>
  )
}
