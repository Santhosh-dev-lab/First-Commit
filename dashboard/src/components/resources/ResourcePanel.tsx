"use client"

import { useResources } from "@/lib/api/client"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { ProvenanceChip } from "@/components/ui/ProvenanceChip"

export function ResourcePanel() {
  const { data: resources, error } = useResources()

  if (error) return <div className="text-red-500 font-mono text-xs">Failed to load resources</div>
  if (!resources) return <div className="text-white/50 font-mono text-xs">Loading resources...</div>

  // Mocking the unmet / requested fields until backend provides them directly in `/api/resources`
  // as per the API baseline, we only have tank_volume_l for now, but we will structure it for the requested visual layout
  const requested = 0;
  const delivered = 0;
  const unmet = 0; 
  
  const isConstrained = unmet > 0;

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>WATER RESOURCE</CardTitle>
        <ProvenanceChip label="OBSERVED" />
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-6">
          
          <div className="flex items-end gap-2">
            <span className="text-4xl font-mono leading-none">{resources.tank_volume_l.toFixed(1)}</span>
            <span className="text-sm font-mono text-white/50 mb-1">L REMAINING</span>
          </div>

          <div className="space-y-3">
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-xs font-mono text-white/50 uppercase tracking-widest">Requested</span>
              <span className="text-xs font-mono">{requested.toFixed(1)} L</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-xs font-mono text-white/50 uppercase tracking-widest">Delivered</span>
              <span className="text-xs font-mono text-emerald-500">{delivered.toFixed(1)} L</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-xs font-mono text-white/50 uppercase tracking-widest">Unmet Demand</span>
              <span className={`text-xs font-mono ${unmet > 0 ? 'text-red-500' : ''}`}>{unmet.toFixed(1)} L</span>
            </div>
          </div>

          <div className="mt-2">
            {isConstrained ? (
              <div className="text-[10px] font-mono tracking-widest uppercase text-red-500 border border-red-500/20 bg-red-500/10 px-3 py-2 rounded text-center">
                RESOURCE CONSTRAINED
              </div>
            ) : (
              <div className="text-[10px] font-mono tracking-widest uppercase text-emerald-500 border border-emerald-500/20 bg-emerald-500/10 px-3 py-2 rounded text-center">
                RESOURCE CONSERVED
              </div>
            )}
          </div>

        </div>
      </CardContent>
    </Card>
  )
}
