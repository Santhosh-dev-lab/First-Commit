"use client"

import { DashboardSnapshot, PlanResponse } from "@/lib/api/types"
import { Bot, CheckCircle2, Clock } from "lucide-react"

export function AdvisoryWidget({ snapshot }: { snapshot: DashboardSnapshot | null }) {
  if (!snapshot) return null;

  const plans = snapshot.active_plans || [];

  return (
    <div className="w-full h-full flex flex-col bg-[#121212]">
      <div className="px-4 py-3 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-sm text-white/90">AI Advisory & Plans</h3>
        <span className="text-xs text-blue-400 cursor-pointer hover:underline">View All</span>
      </div>
      <div className="flex-1 p-0 overflow-auto">
        {plans.length === 0 ? (
          <div className="flex items-center justify-center h-full text-white/50 text-sm py-8">
            NO ACTIVE PLANS
          </div>
        ) : (
          <ul className="divide-y divide-white/5">
            {plans.map((plan: PlanResponse) => (
              <li key={plan.plan_id} className="p-4 hover:bg-white/[0.02] flex items-start gap-3">
                <div className="p-2 bg-blue-500/10 rounded-full shrink-0">
                  <Bot className="w-4 h-4 text-blue-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white/90 font-medium">Plan {plan.plan_id.slice(0, 8)}</p>
                  <p className="text-xs text-white/50 mt-1">Actions: {plan.actions.length}</p>
                </div>
                <div className="flex items-center gap-1">
                  {plan.execution_status === "PENDING" ? (
                    <Clock className="w-4 h-4 text-yellow-500" />
                  ) : plan.execution_status === "COMPLETED" ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  ) : (
                    <span className="text-xs text-white/50">{plan.execution_status}</span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

