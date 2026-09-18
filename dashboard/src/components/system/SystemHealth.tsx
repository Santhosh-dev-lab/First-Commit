"use client"

export function SystemHealth() {
  const systems = [
    { name: "API Gateway", status: "ONLINE", type: "core" },
    { name: "Simulation Engine", status: "ONLINE", type: "compute" },
    { name: "Digital Twin", status: "SYNCHRONIZED", type: "state" },
    { name: "Safety Engine", status: "ONLINE", type: "security" },
    { name: "Agent Provider", status: "MOCK / BEDROCK", type: "ai" },
    { name: "Crop Registry", status: "ONLINE", type: "data" },
  ]

  return (
    <div className="flex flex-col gap-2">
      {systems.map((sys) => (
        <div key={sys.name} className="flex justify-between items-center p-2 bg-white/[0.02] border border-white/5 rounded">
          <span className="text-xs font-mono text-white/70">{sys.name}</span>
          <span className={`text-[10px] font-mono font-bold uppercase ${
            sys.status === "ONLINE" || sys.status === "SYNCHRONIZED" ? "text-emerald-400" :
            sys.status.includes("MOCK") ? "text-purple-400" :
            "text-amber-400"
          }`}>
            {sys.status}
          </span>
        </div>
      ))}
    </div>
  )
}
