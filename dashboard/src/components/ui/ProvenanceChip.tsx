import { cn } from "@/lib/utils"

interface ProvenanceChipProps {
  label: "OBSERVED" | "COMPUTED" | "SIMULATED" | "ASSUMED" | "CONFIGURED" | "PREDICTED";
  className?: string;
}

const colors = {
  OBSERVED: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
  COMPUTED: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  SIMULATED: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  ASSUMED: "bg-orange-500/10 text-orange-500 border-orange-500/20",
  CONFIGURED: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  PREDICTED: "bg-indigo-500/10 text-indigo-500 border-indigo-500/20",
}

export function ProvenanceChip({ label, className }: ProvenanceChipProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium border tracking-wider",
        colors[label],
        className
      )}
    >
      {label}
    </span>
  )
}
