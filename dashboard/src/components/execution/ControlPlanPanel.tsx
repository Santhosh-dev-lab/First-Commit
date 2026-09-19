"use client"

import { usePlan, approvePlan, rejectPlan, dispatchPlan } from "@/lib/api/client"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { ProvenanceChip } from "@/components/ui/ProvenanceChip"
import { cn } from "@/lib/utils"

export function ControlPlanPanel({ planId }: { planId: string | null }) {
  const { data: plan, error, mutate } = usePlan(planId)

  if (!planId) return (
    <div className="h-full flex flex-col pt-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xs font-mono tracking-widest text-white/50 uppercase">Current Control Plan</h2>
      </div>
      <div className="flex-1 flex items-center justify-center text-xs font-mono text-white/30 uppercase">
        No active control plan
      </div>
    </div>
  )
  
  if (error) return <div className="text-red-500 font-mono text-xs">Failed to load plan</div>
  if (!plan) return <div className="text-white/50 font-mono text-xs">Loading plan...</div>

  const handleApprove = async () => {
    await approvePlan(plan.plan_id)
    await dispatchPlan(plan.plan_id)
    mutate()
  }

  const handleReject = async () => {
    await rejectPlan(plan.plan_id)
    mutate()
  }

  const needsApproval = plan.execution_status === "PROPOSED" || plan.execution_status === "VALIDATED"

  return (
    <div className="h-full flex flex-col pt-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xs font-mono tracking-widest text-white/50 uppercase">Current Control Plan</h2>
      </div>
      
      {/* Horizontal Lifecycle Timeline */}
      <div className="mb-8">
        <div className="flex justify-between relative">
          <div className="absolute top-1/2 left-0 right-0 h-[1px] bg-white/10 -translate-y-1/2 z-0" />
          
          {["PROPOSED", "VALIDATED", "APPROVED", "DISPATCHED", "OBSERVED"].map((stage, idx) => {
            const isActive = plan.execution_status === stage || 
                             (stage === "APPROVED" && ["APPROVED", "DISPATCHED", "ACKNOWLEDGED", "OBSERVED"].includes(plan.execution_status)) ||
                             (stage === "DISPATCHED" && ["DISPATCHED", "ACKNOWLEDGED", "OBSERVED"].includes(plan.execution_status)) ||
                             (stage === "VALIDATED" && ["VALIDATED", "APPROVED", "DISPATCHED", "ACKNOWLEDGED", "OBSERVED"].includes(plan.execution_status));
                             
            const isCurrent = plan.execution_status === stage || (stage === "VALIDATED" && plan.execution_status === "PROPOSED"); // simplified matching

            return (
              <div key={stage} className="relative z-10 flex flex-col items-center gap-2">
                <div className={`w-3 h-3 rounded-full border-2 ${
                  plan.execution_status === "REJECTED" ? "bg-red-500 border-red-900" :
                  isActive ? "bg-emerald-500 border-emerald-900" : "bg-[#111] border-white/20"
                }`} />
                <span className={`text-[8px] font-mono tracking-widest uppercase ${
                  isActive ? "text-emerald-400" : "text-white/30"
                }`}>
                  {stage}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      <div className="flex-1">
        {plan.actions.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-blue-400">💧</span>
              <span className="text-white font-bold">{plan.actions[0].action_type}: {(plan.actions[0].target_id || plan.actions[0].actuator_id).replace("_", " ")}</span>
            </div>
            
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div>
                <div className="text-[9px] text-white/40 font-mono uppercase mb-1">Target</div>
                <div className="text-white font-mono">{plan.actions[0].value ?? plan.actions[0].target_value} L</div>
              </div>
              <div>
                <div className="text-[9px] text-white/40 font-mono uppercase mb-1">Duration</div>
                <div className="text-white font-mono">{plan.actions[0].duration_minutes ?? Math.round(plan.actions[0].duration_s / 60)}m</div>
              </div>
              <div>
                <div className="text-[9px] text-white/40 font-mono uppercase mb-1">Exp Moisture</div>
                <div className="text-emerald-400 font-mono">+8.5%</div>
              </div>
              <div>
                <div className="text-[9px] text-white/40 font-mono uppercase mb-1">Exp Stress</div>
                <div className="text-emerald-400 font-mono">-0.15</div>
              </div>
            </div>

            {needsApproval && (
              <div className="mt-8 border border-amber-500/30 bg-amber-500/5 p-4 rounded-lg">
                <div className="text-[10px] font-mono text-amber-500 tracking-widest uppercase mb-4 text-center">
                  Approval Required
                </div>
                <div className="flex gap-4">
                  <button 
                    onClick={handleApprove}
                    className="flex-1 py-2 bg-emerald-600/20 border border-emerald-500/50 text-emerald-400 font-mono text-xs rounded hover:bg-emerald-600/40 transition-colors flex items-center justify-center gap-2 uppercase tracking-widest"
                  >
                    [ Approve Plan ]
                  </button>
                  <button 
                    onClick={handleReject}
                    className="flex-1 py-2 bg-red-900/20 border border-red-500/50 text-red-500 font-mono text-xs rounded hover:bg-red-900/40 transition-colors flex items-center justify-center gap-2 uppercase tracking-widest"
                  >
                    [ Reject Plan ]
                  </button>
                </div>
              </div>
            )}
            
            {plan.execution_status === "REJECTED" && (
               <div className="mt-8 border border-red-500/30 bg-red-500/5 p-4 rounded-lg text-center">
                 <div className="text-[10px] font-mono text-red-500 tracking-widest uppercase">
                   Plan Rejected by Operator
                 </div>
               </div>
            )}
          </div>
        )}

        <div className="mt-auto">
          <a href="#" className="text-[10px] font-mono text-blue-400 hover:text-blue-300">View Full Plan Details →</a>
        </div>
      </div>
    </div>
  )
}
