"use client"

import { useState } from "react"
import { useAgentTrace, submitIntent } from "@/lib/api/client"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { ProvenanceChip } from "@/components/ui/ProvenanceChip"

export function AgentActivity({ onPlanCreated }: { onPlanCreated: (planId: string) => void }) {
  const [intent, setIntent] = useState("")
  const [runId, setRunId] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const { data: trace } = useAgentTrace(runId)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!intent.trim()) return
    
    setIsSubmitting(true)
    try {
      const res = await submitIntent({ text: intent, zone_id: "zone_1" })
      onPlanCreated(res.plan_id)
      // Mock setting a runId to trigger the trace
      setRunId(res.plan_id)
    } catch (err) {
      console.error(err)
    } finally {
      setIsSubmitting(false)
      setIntent("")
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xs font-mono tracking-widest text-white/50 uppercase">Agent Activity</h2>
        <a href="#" className="text-[10px] font-mono text-blue-400 hover:text-blue-300">View All →</a>
      </div>

      <form onSubmit={handleSubmit} className="mb-6">
        <input 
          type="text" 
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          placeholder="Enter operational objective (e.g. Reduce water consumption...)"
          className="w-full bg-[#111] border border-white/10 rounded px-3 py-2 text-[10px] font-mono text-white focus:outline-none focus:border-blue-500/50 transition-colors placeholder:text-white/20"
          disabled={isSubmitting}
        />
      </form>

      {/* Workflow Diagram */}
      <div className="mb-6 p-4 border border-white/5 bg-white/[0.02] rounded-lg">
        <div className="flex items-center justify-between text-[8px] font-mono tracking-widest text-white/40 uppercase mb-2">
          <span>Agent Workflow Pipeline</span>
          <span className="text-emerald-500 bg-emerald-500/10 px-1 py-0.5 rounded">ACTIVE</span>
        </div>
        <div className="flex justify-between items-center mt-4 px-2">
          <div className="flex flex-col items-center">
            <div className={`w-6 h-6 rounded flex items-center justify-center border ${runId ? "border-blue-500/50 bg-blue-500/10 text-blue-400" : "border-white/10 bg-[#111] text-white/30"}`}>1</div>
            <span className="text-[8px] font-mono mt-2 text-white/50 text-center">INTENT<br/>AGENT</span>
          </div>
          <div className={`h-[1px] flex-1 mx-2 ${runId ? "bg-blue-500/30" : "bg-white/10"}`} />
          <div className="flex flex-col items-center">
            <div className={`w-6 h-6 rounded flex items-center justify-center border ${runId ? "border-purple-500/50 bg-purple-500/10 text-purple-400" : "border-white/10 bg-[#111] text-white/30"}`}>2</div>
            <span className="text-[8px] font-mono mt-2 text-white/50 text-center">PLANNING<br/>AGENT</span>
          </div>
          <div className={`h-[1px] flex-1 mx-2 ${runId ? "bg-purple-500/30" : "bg-white/10"}`} />
          <div className="flex flex-col items-center">
            <div className={`w-6 h-6 rounded flex items-center justify-center border ${runId ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-400" : "border-white/10 bg-[#111] text-white/30"}`}>3</div>
            <span className="text-[8px] font-mono mt-2 text-white/50 text-center">SAFETY<br/>CHECK</span>
          </div>
          <div className={`h-[1px] flex-1 mx-2 ${runId ? "bg-emerald-500/30" : "bg-white/10"}`} />
          <div className="flex flex-col items-center">
            <div className={`w-6 h-6 rounded flex items-center justify-center border ${runId ? "border-amber-500/50 bg-amber-500/10 text-amber-400" : "border-white/10 bg-[#111] text-white/30"}`}>4</div>
            <span className="text-[8px] font-mono mt-2 text-white/50 text-center">HUMAN<br/>APPROVAL</span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 relative">
        {!trace && !isSubmitting ? (
           <div className="text-[10px] font-mono text-white/30 pt-4 text-center">System idle. Awaiting intent.</div>
        ) : (
          <div className="relative border-l border-white/10 ml-2 mt-2 space-y-6 pb-4">
            
            {/* Timeline Item 1 */}
            <div className="relative pl-6">
              <div className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-[#ff5a5a] border-4 border-[#0a0a0a]" />
              <div className="flex gap-4">
                <span className="text-[10px] font-mono text-white/40 w-12 pt-1">Just now</span>
                <div>
                  <h4 className="text-xs font-bold text-white mb-1">Planning Agent</h4>
                  <p className="text-[10px] text-white/60 font-mono">Generated irrigation plan for Zone 1</p>
                  {trace?.decision && (
                    <p className="text-[10px] text-white/80 font-mono mt-2 bg-white/5 p-2 rounded border border-white/5">
                      {trace.decision}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Timeline Item 2 */}
            <div className="relative pl-6">
              <div className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-emerald-500 border-4 border-[#0a0a0a]" />
              <div className="flex gap-4">
                <span className="text-[10px] font-mono text-white/40 w-12 pt-1">-2s</span>
                <div>
                  <h4 className="text-xs font-bold text-white mb-1">Safety Check</h4>
                  <p className="text-[10px] text-white/60 font-mono">All checks passed</p>
                </div>
              </div>
            </div>

            {/* Timeline Item 3 */}
            <div className="relative pl-6">
              <div className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-emerald-500 border-4 border-[#0a0a0a]" />
              <div className="flex gap-4">
                <span className="text-[10px] font-mono text-white/40 w-12 pt-1">-6s</span>
                <div>
                  <h4 className="text-xs font-bold text-white mb-1">Simulation</h4>
                  <p className="text-[10px] text-white/60 font-mono">Evaluated 3 scenarios using Digital Twin</p>
                </div>
              </div>
            </div>

            {/* Timeline Item 4 */}
            <div className="relative pl-6">
              <div className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-blue-500 border-4 border-[#0a0a0a]" />
              <div className="flex gap-4">
                <span className="text-[10px] font-mono text-white/40 w-12 pt-1">-12s</span>
                <div>
                  <h4 className="text-xs font-bold text-white mb-1">Intent Agent</h4>
                  <p className="text-[10px] text-white/60 font-mono">Processed objective</p>
                </div>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  )
}
