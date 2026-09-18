import { cn } from "@/lib/utils"

export function Card({ className, children }: { className?: string, children: React.ReactNode }) {
  return (
    <div className={cn("bg-[#111111] border border-white/10 rounded shadow-sm", className)}>
      {children}
    </div>
  )
}

export function CardHeader({ className, children }: { className?: string, children: React.ReactNode }) {
  return (
    <div className={cn("px-4 py-3 border-b border-white/10 flex items-center justify-between", className)}>
      {children}
    </div>
  )
}

export function CardTitle({ className, children }: { className?: string, children: React.ReactNode }) {
  return (
    <h3 className={cn("text-xs font-mono tracking-widest text-white/50 uppercase", className)}>
      {children}
    </h3>
  )
}

export function CardContent({ className, children }: { className?: string, children: React.ReactNode }) {
  return (
    <div className={cn("p-4", className)}>
      {children}
    </div>
  )
}
