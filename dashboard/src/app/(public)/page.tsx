"use client"

import Link from "next/link"
import { ArrowRight, Bot, Database, Server, ShieldCheck, Activity, LineChart, ChevronDown, MoveDown } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans selection:bg-emerald-500/30">
      {/* Navigation */}
      <nav className="absolute top-0 left-0 right-0 z-50 text-white border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 text-white">
              <path d="M12 2L2 12L12 22L22 12L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12H22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="hidden lg:flex items-center gap-8 text-sm font-medium">
            <Link href="#products" className="flex items-center gap-1 hover:text-white/80">Products <ChevronDown className="w-3 h-3" /></Link>
            <Link href="#focus-crops" className="flex items-center gap-1 hover:text-white/80">Focus Crops <ChevronDown className="w-3 h-3" /></Link>
            <Link href="#use-cases" className="hover:text-white/80">Use Cases</Link>
            <Link href="#network" className="flex items-center gap-1 hover:text-white/80">Network <ChevronDown className="w-3 h-3" /></Link>
            <Link href="#learn-more" className="flex items-center gap-1 hover:text-white/80">Learn More <ChevronDown className="w-3 h-3" /></Link>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/login" className="text-sm font-medium hover:text-white/80">Log in</Link>
            <Link href="/register" className="text-sm font-medium bg-white text-black px-5 py-2.5 rounded-full hover:bg-gray-100 transition-colors">
              Get a Demo
            </Link>
          </div>
        </div>
      </nav>

      <main>
        {/* Hero Section */}
        <section className="relative h-screen min-h-[700px] flex flex-col justify-end pb-12 pt-24 overflow-hidden">
          {/* Background Image */}
          <div className="absolute inset-0 z-0">
            <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/10 to-black/60 z-10 mix-blend-multiply pointer-events-none" />
            <img src="/hero-bg.jpg" alt="Agricultural field from above" className="w-full h-full object-cover" />
          </div>
          
          <div className="relative z-20 max-w-7xl mx-auto px-6 w-full flex flex-col h-full justify-between">
            {/* Top area empty for balance */}
            <div className="flex-1"></div>
            
            {/* Lower area with text and buttons */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-end mb-8">
              
              <div className="lg:col-span-8 order-2 lg:order-1">
                <h1 className="text-5xl md:text-6xl lg:text-[76px] font-medium leading-[1.1] tracking-tight">
                  The Most <span className="italic font-light border-b-2 pb-1 border-white">Powerful</span> Field Analytics Platform For Crop Insights
                </h1>
              </div>
              
              <div className="lg:col-span-4 order-1 lg:order-2 lg:pb-12 space-y-6">
                <p className="text-base text-white/90 leading-relaxed max-w-sm ml-auto">
                  We developed an easy-to-use, easy-to-operate, comprehensive system for gaining insights from drones and satellites. Compatible with drones & machinery, our platform delivers on-the-farm data assimilation.
                </p>
                <div className="flex flex-wrap items-center gap-4 ml-auto max-w-sm">
                  <Link href="/register" className="inline-flex items-center justify-center px-6 py-3 text-sm font-medium rounded-full text-black bg-white hover:bg-gray-100 transition-colors">
                    Free Trial
                  </Link>
                  <Link href="#product" className="inline-flex items-center justify-center px-6 py-3 border border-white/40 text-sm font-medium rounded-full text-white hover:bg-white/10 transition-colors">
                    See All Product
                  </Link>
                </div>
              </div>
            </div>

            {/* Bottom Right Explore */}
            <div className="flex justify-end text-sm font-medium text-white/80">
              <Link href="#product" className="flex items-center gap-2 hover:text-white transition-colors">
                Explore More <MoveDown className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* Why PHYSICA / Product Explanation */}
        <section id="product" className="py-24 border-t border-white/5 bg-[#0a0a0a]">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl font-light tracking-tight mb-4">Why PHYSICA?</h2>
              <p className="text-white/60 text-lg">Traditional automation relies on hardcoded rules (Sensor → Rule → Actuator). PHYSICA elevates automation to intentional control through reasoning and physical simulation.</p>
            </div>
            
            <div className="p-8 border border-white/10 rounded-2xl bg-black overflow-x-auto">
              <div className="flex items-center gap-4 min-w-max pb-4 text-sm font-medium text-white/80">
                <div className="px-4 py-2 border border-white/10 rounded bg-[#121212]">Human Intent</div>
                <ArrowRight className="w-4 h-4 text-white/30" />
                <div className="px-4 py-2 border border-white/10 rounded bg-[#121212]">Agent Reasoning</div>
                <ArrowRight className="w-4 h-4 text-white/30" />
                <div className="px-4 py-2 border border-blue-500/30 rounded bg-blue-500/10 text-blue-400">Physics & Digital Twin</div>
                <ArrowRight className="w-4 h-4 text-white/30" />
                <div className="px-4 py-2 border border-white/10 rounded bg-[#121212]">Simulation</div>
                <ArrowRight className="w-4 h-4 text-white/30" />
                <div className="px-4 py-2 border border-emerald-500/30 rounded bg-emerald-500/10 text-emerald-400">Safety Verification</div>
                <ArrowRight className="w-4 h-4 text-white/30" />
                <div className="px-4 py-2 border border-white/10 rounded bg-[#121212]">Human Approval</div>
                <ArrowRight className="w-4 h-4 text-white/30" />
                <div className="px-4 py-2 border border-white/10 rounded bg-[#121212]">Edge Execution</div>
              </div>
            </div>
          </div>
        </section>

        {/* Core Capabilities */}
        <section className="py-24 border-t border-white/5">
          <div className="max-w-7xl mx-auto px-6">
            <h2 className="text-3xl font-light tracking-tight mb-12 text-center">Core Capabilities</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { title: "Agentic Reasoning", desc: "Agents interpret physical-world objectives and formulate high-level strategies.", icon: Bot },
                { title: "Physical Models", desc: "Deterministic differential equations represent strict physical and biological behavior.", icon: Database },
                { title: "Simulation", desc: "Evaluate strategies through fast-forward state evolution before executing in reality.", icon: Activity },
                { title: "Optimization", desc: "Search the action space for resource-efficient and yield-maximizing control strategies.", icon: LineChart },
                { title: "Safety Verification", desc: "Deterministic safety boundaries authorize or reject physical actions before they happen.", icon: ShieldCheck },
                { title: "Edge Execution", desc: "Approved plans are translated into precise, timed control commands for physical actuators.", icon: Server },
              ].map((cap, i) => (
                <div key={i} className="p-6 border border-white/10 rounded-xl bg-[#0a0a0a] hover:bg-[#121212] transition-colors group">
                  <cap.icon className="w-8 h-8 text-white/40 mb-4 group-hover:text-emerald-400 transition-colors" />
                  <h3 className="text-lg font-medium mb-2">{cap.title}</h3>
                  <p className="text-sm text-white/60 leading-relaxed">{cap.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Controlled Environment Agriculture */}
        <section className="py-24 border-t border-white/5 bg-[#0a0a0a]">
          <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl font-light tracking-tight mb-6">Built for Physical Systems</h2>
              <p className="text-lg text-white/60 mb-6">
                PHYSICA is currently applied to Controlled-Environment Agriculture (CEA) as its primary validation domain. By modeling plant biology and polyhouse thermodynamics, PHYSICA optimizes irrigation, climate, and resources.
              </p>
              <ul className="space-y-4">
                {['Crop-agnostic architecture (Tomato, Lettuce, Cucumber, Strawberry)', 'Multi-zone microclimate control', 'Water and energy resource tracking', 'Continuous sensor telemetry feedback'].map((item, i) => (
                  <li key={i} className="flex items-start gap-3 text-white/80">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="grid grid-cols-2 gap-4">
               <div className="h-32 border border-white/10 rounded-xl bg-black flex flex-col justify-center items-center p-4 text-center">
                 <div className="text-2xl font-light text-white mb-1">Dwarf Tomato</div>
                 <div className="text-xs text-emerald-400">Solanum lycopersicum</div>
               </div>
               <div className="h-32 border border-white/10 rounded-xl bg-black flex flex-col justify-center items-center p-4 text-center">
                 <div className="text-2xl font-light text-white mb-1">Lettuce</div>
                 <div className="text-xs text-emerald-400">Lactuca sativa</div>
               </div>
               <div className="h-32 border border-white/10 rounded-xl bg-black flex flex-col justify-center items-center p-4 text-center">
                 <div className="text-2xl font-light text-white mb-1">Cucumber</div>
                 <div className="text-xs text-emerald-400">Cucumis sativus</div>
               </div>
               <div className="h-32 border border-white/10 rounded-xl bg-black flex flex-col justify-center items-center p-4 text-center">
                 <div className="text-2xl font-light text-white mb-1">Strawberry</div>
                 <div className="text-xs text-emerald-400">Fragaria x ananassa</div>
               </div>
            </div>
          </div>
        </section>

        {/* Safety */}
        <section className="py-24 border-t border-white/5">
          <div className="max-w-7xl mx-auto px-6 text-center max-w-4xl">
            <ShieldCheck className="w-16 h-16 text-emerald-400 mx-auto mb-6" />
            <h2 className="text-3xl md:text-5xl font-light tracking-tight mb-6">Agents reason. <br/> Deterministic systems authorize.</h2>
            <p className="text-xl text-white/60 mb-10">
              Large Language Models and Agents do not directly control actuators in PHYSICA. Every proposal is subjected to a strict deterministic validation layer ensuring physical limits and safety constraints are never breached, followed by mandatory human approval for critical actions.
            </p>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-24 border-t border-white/5 bg-[#0a0a0a]">
          <div className="max-w-7xl mx-auto px-6">
            <h2 className="text-3xl font-light tracking-tight mb-16 text-center">How It Works</h2>
            <div className="grid md:grid-cols-4 gap-8">
              {[
                { step: "01", title: "DEFINE", desc: "Express a physical objective in natural language or operational targets." },
                { step: "02", title: "ANALYZE", desc: "PHYSICA agents reason over physical state, history, and resource constraints." },
                { step: "03", title: "VERIFY", desc: "Candidate strategies are simulated on the digital twin and safety checked." },
                { step: "04", title: "EXECUTE", desc: "Approved control plans are dispatched as discrete commands to the physical system." },
              ].map((s, i) => (
                <div key={i} className="relative">
                  <div className="text-5xl font-bold text-white/5 mb-4">{s.step}</div>
                  <h3 className="text-lg font-medium mb-3">{s.title}</h3>
                  <p className="text-sm text-white/60 leading-relaxed">{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-32 border-t border-white/5 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-[#050505] to-emerald-900/10 -z-10" />
          <div className="max-w-4xl mx-auto px-6 text-center">
            <h2 className="text-4xl md:text-5xl font-light tracking-tight mb-8">Build systems that can reason about the physical world.</h2>
            <Link href="/register" className="inline-flex items-center justify-center px-8 py-4 border border-transparent text-lg font-medium rounded-lg text-black bg-white hover:bg-gray-100 transition-colors">
              Get Started
            </Link>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 bg-black">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-4 gap-8 text-sm">
          <div className="col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-6 h-6 bg-white text-black rounded flex items-center justify-center font-bold text-[10px]">PH</div>
              <span className="font-semibold tracking-wider">PHYSICA</span>
            </div>
            <p className="text-white/50 mb-4 max-w-xs">A Compiler for Physical Reality.</p>
          </div>
          <div>
            <h4 className="font-medium mb-4">Platform</h4>
            <ul className="space-y-2 text-white/50">
              <li><Link href="#product" className="hover:text-white transition-colors">Product</Link></li>
              <li><Link href="#technology" className="hover:text-white transition-colors">Technology</Link></li>
              <li><Link href="#research" className="hover:text-white transition-colors">Research</Link></li>
              <li><Link href="#about" className="hover:text-white transition-colors">About</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-4">Legal</h4>
            <ul className="space-y-2 text-white/50">
              <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-6 mt-12 pt-8 border-t border-white/5 text-xs text-white/30">
          © {new Date().getFullYear()} PHYSICA. All rights reserved.
        </div>
      </footer>
    </div>
  )
}

function CheckCircle2(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  )
}
