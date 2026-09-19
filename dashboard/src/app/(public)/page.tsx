"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import Link from "next/link"
import {
  ArrowRight,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Droplets,
  Sun,
  Wind,
  Thermometer,
  ShieldCheck,
  Zap,
  Activity,
  Layers,
  Sprout,
  BarChart3,
  Star,
  Plus,
  Minus,
  ArrowUpRight,
  TrendingUp,
  Cpu,
  Compass,
  Sparkles,
  Calendar,
  MapPin,
  CloudRain,
  Sliders,
} from "lucide-react"

export default function AgroviaLandingPage() {
  // 1. Accordion State & Sticky Scroll-driven Controller for Feature Section
  const solutionsRef = useRef<HTMLDivElement>(null)
  const itemRefs = useRef<(HTMLDivElement | null)[]>([])
  const [activeAccordion, setActiveAccordion] = useState(0)
  const [openAccordions, setOpenAccordions] = useState<number[]>([0])

  // 2. Tab Controller State for Dashboard Feature Showcase
  const [activeTab, setActiveTab] = useState("overview")

  // 3. FAQ Accordion State
  const [openFaq, setOpenFaq] = useState<number | null>(0)

  // 4. Cursor Movement & Parallax State
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const [cursorPos, setCursorPos] = useState({ x: -100, y: -100 })
  const [isHovered, setIsHovered] = useState(false)

  // 5. Scroll-Driven Word Highlight State
  const narrativeRef = useRef<HTMLDivElement>(null)
  const [scrollProgress, setScrollProgress] = useState(0)

  const narrativeWords = [
    "Our", "platform", "is", "built", "to", "support", "farmers,", "agribusinesses,", "and", "agricultural", "innovators", "by", "delivering", "practical", "tools", "that", "respect", "the", "land", "while", "improving", "productivity."
  ]

  // Track scroll position for bidirectional scroll-driven text word highlight (up and down)
  useEffect(() => {
    const handleScroll = () => {
      if (!narrativeRef.current) return
      const rect = narrativeRef.current.getBoundingClientRect()
      const windowHeight = window.innerHeight
      const start = windowHeight * 0.92
      const end = windowHeight * 0.12
      const raw = (start - rect.top) / (start - end)
      const clamped = Math.min(Math.max(raw, 0), 1)
      setScrollProgress(clamped)
    }

    window.addEventListener("scroll", handleScroll, { passive: true })
    handleScroll()
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  // Accordion Item Click Toggle Handler
  const toggleAccordion = (id: number) => {
    setActiveAccordion(id)
  }

  // Track cursor position globally for glowing light spotlight
  useEffect(() => {
    const handleGlobalMouseMove = (e: MouseEvent) => {
      setCursorPos({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener("mousemove", handleGlobalMouseMove)
    return () => window.removeEventListener("mousemove", handleGlobalMouseMove)
  }, [])

  // Handle Hero Mouse Move for 3D Parallax Movement
  const handleHeroMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = (e.clientX - rect.left - rect.width / 2) / (rect.width / 2)
    const y = (e.clientY - rect.top - rect.height / 2) / (rect.height / 2)
    setMousePos({ x, y })
    setIsHovered(true)
  }, [])

  const handleHeroMouseLeave = useCallback(() => {
    setMousePos({ x: 0, y: 0 })
    setIsHovered(false)
  }, [])

  const featureAccordionItems = [
    {
      id: 0,
      title: "Proven Farm Productivity",
      tagline: "+35% Yield Improvement",
      desc: "Empower your agricultural operations with data-driven yield acceleration and real-time state estimation. Our deterministic physics engine predicts physiological growth bottlenecks before they occur.",
      image: "/agrovia-hero.jpg",
      metrics: ["+35% Biomass Growth", "Real-time Telemetry", "Automated Feedback"],
    },
    {
      id: 1,
      title: "Intelligent Crop Optimization",
      tagline: "Biological Micro-Climate Tuning",
      desc: "Customized micro-environment schedules tailored per crop cultivar (Dwarf Tomato, Strawberry, Microgreens, Lettuce). Automatically adjusts PAR light intensity, transpiration, and CO2 enrichment.",
      image: "/agrovia-crop.jpg",
      metrics: ["Crop-Agnostic Engine", "Optimal PAR Control", "Zero-Stress Target"],
    },
    {
      id: 2,
      title: "Seamless Farm System Integration",
      tagline: "Universal IoT Edge Bridge",
      desc: "Plug-and-play IoT hardware abstraction connecting sensors, pumps, valves, and edge gateways via industrial protocols including MQTT, Modbus, and OPC-UA without breaking existing infrastructure.",
      image: "/agrovia-drone.jpg",
      metrics: ["MQTT / Modbus Native", "Sub-second Latency", "Edge Fail-Safe"],
    },
    {
      id: 3,
      title: "Smart Water & Resource Management",
      tagline: "30% Water Conservation",
      desc: "Precision micro-drip irrigation models calculate exact evapotranspiration demand, drastically reducing water usage and fertilizer runoff while protecting groundwater reserves.",
      image: "/agrovia-water.jpg",
      metrics: ["30% Less Water Use", "Evapotranspiration Math", "Tank Auto-Balancing"],
    },
  ]

  const faqs = [
    {
      q: "How does PHYSICA guarantee physical hardware safety?",
      a: "PHYSICA enforces a strict, crop-independent Safety Engine between the AI planning layer and physical edge hardware. Every proposed control plan is verified against physical constraints (temperature, pressure, equipment rate limits) before actuation. If a plan violates safety limits, it is instantly rejected.",
    },
    {
      q: "Can PHYSICA integrate with existing polyhouse equipment?",
      a: "Yes. PHYSICA provides native Edge Gateway abstraction supporting standard industrial IoT protocols including MQTT, Modbus, and OPC-UA. This allows seamless integration with legacy pumps, solenoids, HVAC units, and sensor arrays.",
    },
    {
      q: "What crops are supported out-of-the-box?",
      a: "PHYSICA includes built-in physiological crop profiles for Dwarf Tomato, Lettuce, Cucumber, Microgreens, and Strawberry. Custom crop profiles can easily be defined in the CropRegistry.",
    },
    {
      q: "How does the AI model optimize water and energy consumption?",
      a: "Our Scenario Optimizer runs fast-forward deterministic physical simulations evaluating candidate control strategies against baseline heuristics to find Pareto-optimal paths that maximize biomass output while minimizing water and electricity usage.",
    },
  ]

  return (
    <div className="min-h-screen bg-[#F8FAF8] text-[#1B1C1E] font-sans-body selection:bg-[#2E7D32]/20 selection:text-[#2E7D32] relative overflow-x-hidden">
      
      {/* Dynamic Cursor Glowing Spotlight Following Mouse */}
      <div
        className="pointer-events-none fixed z-50 rounded-full transition-opacity duration-500 opacity-60 blur-3xl hidden md:block"
        style={{
          left: `${cursorPos.x - 150}px`,
          top: `${cursorPos.y - 150}px`,
          width: "300px",
          height: "300px",
          background: "radial-gradient(circle, rgba(76,175,80,0.25) 0%, rgba(46,125,50,0.05) 70%, transparent 100%)",
        }}
      />

      {/* ========================================== */}
      {/* 1. TOP NAVIGATION OVERLAY (FULL BLEED)     */}
      {/* ========================================== */}
      <header className="absolute top-0 left-0 right-0 z-50 pt-6 px-6 md:px-12">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          
          {/* Left Brand Logo */}
          <Link href="/" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
            <div className="w-9 h-9 rounded-xl bg-[#A3E635] flex items-center justify-center text-black font-bold shadow-md">
              <Sprout className="w-5 h-5 text-black" />
            </div>
            <span className="font-sans font-bold text-xl text-white tracking-tight">
              Agrovia <span className="text-[#A3E635] font-mono text-xs uppercase tracking-widest font-semibold ml-1">Physica</span>
            </span>
          </Link>

          {/* Center Glass Pill Navigation */}
          <nav className="hidden md:flex items-center gap-1 bg-white/15 backdrop-blur-md px-4 py-2 rounded-full border border-white/20 text-xs font-semibold text-white/90">
            <Link href="#hero" className="flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-white/20 text-white font-bold">
              <span className="w-2 h-2 rounded-full bg-[#A3E635]" />
              <span>Home</span>
            </Link>
            <Link href="#about" className="px-4 py-1.5 rounded-full hover:text-white hover:bg-white/10 transition-all">
              About Us
            </Link>
            <Link href="#solutions" className="px-4 py-1.5 rounded-full hover:text-white hover:bg-white/10 transition-all">
              Solutions
            </Link>
            <Link href="#showcase" className="px-4 py-1.5 rounded-full hover:text-white hover:bg-white/10 transition-all">
              Investors
            </Link>
            <Link href="#metrics" className="px-4 py-1.5 rounded-full hover:text-white hover:bg-white/10 transition-all">
              Success Story
            </Link>
          </nav>

          {/* Right Action Button */}
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="hidden sm:inline-flex text-xs font-bold text-white hover:text-[#A3E635] transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="bg-white hover:bg-gray-100 text-[#1B1C1E] text-xs font-bold px-6 py-3 rounded-full shadow-lg transition-all hover:scale-105"
            >
              Contact Us
            </Link>
          </div>
        </div>
      </header>

      <main>
        
        {/* ========================================== */}
        {/* HERO SECTION — FULL BLEED LAYOUT          */}
        {/* ========================================== */}
        <section
          id="hero"
          onMouseMove={handleHeroMouseMove}
          onMouseLeave={handleHeroMouseLeave}
          className="relative w-full min-h-screen flex flex-col justify-between overflow-hidden bg-black text-white"
        >
          {/* Full Bleed Background Image */}
          <div className="absolute inset-0 z-0">
            <img
              src="/agrovia-hero.jpg"
              alt="Agrovia Smart Agriculture Full Bleed"
              className="w-full h-full object-cover transition-transform duration-300 ease-out"
              style={{
                transform: `scale(1.08) translate(${mousePos.x * -16}px, ${mousePos.y * -16}px)`,
              }}
            />
            {/* Dark Tint Overlay for Text Legibility */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-black/30 z-10" />
          </div>

          {/* Spacer for Top Header Navigation */}
          <div className="h-28"></div>

          {/* Hero Main Content Overlay (Full Bleed Aligned) */}
          <div className="relative z-20 max-w-7xl mx-auto px-6 md:px-12 w-full flex-1 flex flex-col justify-end pb-16">
            
            {/* Top Pill Tag */}
            <div className="mb-6">
              <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur-md border border-white/20 px-4 py-2 rounded-full text-white text-xs font-medium">
                <span className="w-2 h-2 rounded-full bg-[#A3E635] animate-ping" />
                <Sparkles className="w-3.5 h-3.5 text-[#A3E635]" />
                <span>AI-Powered Autonomous Polyhouse Compiler</span>
              </div>
            </div>

            {/* Main Headline */}
            <h1
              className="font-serif-display text-4xl sm:text-6xl md:text-7xl lg:text-[84px] font-normal text-white leading-[1.05] tracking-tight mb-6 transition-transform duration-200"
              style={{
                transform: `translate(${mousePos.x * 10}px, ${mousePos.y * 10}px)`,
              }}
            >
              Smart Farming for <br />
              <span className="italic font-light text-white/90">Future Generations</span>
            </h1>

            {/* Subtitle Paragraph */}
            <p className="text-base sm:text-lg text-white/80 font-light leading-relaxed max-w-xl mb-10">
              Send, receive, and track your agricultural outcomes in one secure platform built for speed, clarity, and everyday physical control.
            </p>

            {/* Action Buttons Group */}
            <div className="flex flex-wrap items-center gap-4 mb-16">
              <Link
                href="/register"
                className="inline-flex items-center gap-2 bg-[#A3E635] hover:bg-[#86efac] text-black font-bold text-sm px-8 py-4 rounded-full shadow-lg transition-all hover:scale-105"
              >
                <span>Start Investing</span>
                <ArrowUpRight className="w-4 h-4 text-black" />
              </Link>
              <Link
                href="#solutions"
                className="inline-flex items-center gap-2 border border-white/40 hover:border-white bg-white/10 backdrop-blur-md text-white text-sm font-semibold px-8 py-4 rounded-full transition-all hover:bg-white/20"
              >
                <span>Meet the Farmers</span>
              </Link>
            </div>

            {/* Hero Bottom Bar */}
            <div className="flex flex-wrap items-center justify-between gap-6 pt-6 border-t border-white/20">
              
              {/* Scroll Pill Left */}
              <a href="#brands" className="flex items-center gap-2 text-white/80 text-xs font-mono uppercase tracking-widest hover:text-white transition-colors">
                <span>SCROLL</span>
                <ChevronDown className="w-4 h-4 animate-bounce text-[#A3E635]" />
              </a>

              {/* Rating Widget Right */}
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                  <span className="font-bold text-sm text-white">4.9</span>
                </div>
                <div className="flex items-center gap-3 bg-white/15 backdrop-blur-md border border-white/20 px-4 py-2 rounded-full">
                  <div className="flex -space-x-2">
                    <img className="w-7 h-7 rounded-full object-cover shadow-sm" src="/agrovia-crop.jpg" alt="Farmer" />
                    <img className="w-7 h-7 rounded-full object-cover shadow-sm" src="/agrovia-water.jpg" alt="Farmer" />
                    <img className="w-7 h-7 rounded-full object-cover shadow-sm" src="/agrovia-drone.jpg" alt="Farmer" />
                  </div>
                  <span className="text-xs font-semibold text-white">10k+ Farmers</span>
                </div>
              </div>

            </div>

          </div>
        </section>

        {/* ========================================== */}
        {/* BRAND PARTNER LOGO STRIP (ANIMATED MARQUEE)*/}
        {/* ========================================== */}
        <section id="brands" className="w-full bg-white py-10 border-b border-black/5 overflow-hidden">
          <div className="max-w-7xl mx-auto px-6 md:px-12 flex items-center justify-between gap-8">
            
            <div className="text-xs font-bold text-[#1B1C1E]/50 uppercase tracking-wider shrink-0 max-w-[150px] z-10 bg-white pr-4">
              Trusted by <span className="text-[#1B1C1E]">thousand companies</span> in the world
            </div>

            {/* Continuous Marquee Ticker */}
            <div className="overflow-hidden flex-1 relative">
              <div className="flex items-center gap-12 text-[#1B1C1E]/70 font-mono font-bold text-sm sm:text-base whitespace-nowrap animate-marquee">
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer inline-flex items-center gap-1">CHASE <span className="text-[#2E7D32] animate-ping">●</span></span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">JOHN DEERE</span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">Z LEADER*</span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">Kubota</span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">GLEANER</span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">BAYER</span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">VALMOT</span>

                {/* Repeated items for seamless infinite scroll */}
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer inline-flex items-center gap-1">CHASE <span className="text-[#2E7D32] animate-ping">●</span></span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">JOHN DEERE</span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">Z LEADER*</span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">Kubota</span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">GLEANER</span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">BAYER</span>
                <span className="hover:text-[#2E7D32] hover:scale-110 transition-all cursor-pointer">VALMOT</span>
              </div>
            </div>

          </div>
        </section>

        {/* ========================================== */}
        {/* INTRO NARRATIVE SECTION (SCROLL ANIMATED)  */}
        {/* ========================================== */}
        <section ref={narrativeRef} id="about" className="relative py-20 md:py-28 px-6 md:px-12 max-w-6xl mx-auto text-left overflow-hidden">
          
          {/* Soft Ambient Glow */}
          <div className="absolute top-1/2 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#2E7D32]/10 rounded-full blur-3xl pointer-events-none animate-pulse-glow" />

          <div className="mb-8 relative z-10">
            <span className="inline-flex items-center gap-2.5 bg-[#F3F5F3] hover:bg-[#E8F5E9] text-[#1B1C1E]/80 text-xs font-semibold px-4 py-2 rounded-full border border-black/5 animate-float-slow transition-all shadow-sm">
              <span className="w-2.5 h-2.5 rounded-full bg-[#2E7D32] animate-ping" />
              <span className="font-bold text-[#2E7D32]">Cultiva Legacy</span>
            </span>
          </div>

          <h2 className="relative z-10 font-sans text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-normal text-[#1B1C1E] leading-[1.35] tracking-tight">
            {narrativeWords.map((word, idx) => {
              const totalWords = narrativeWords.length
              const step = 1 / totalWords
              const wordStart = idx * step
              const wordEnd = (idx + 1) * step
              
              // Continuous word progress between 0 and 1
              const rawProgress = (scrollProgress - wordStart) / (wordEnd - wordStart)
              const wordProgress = Math.min(Math.max(rawProgress, 0), 1)

              const opacity = 0.35 + wordProgress * 0.65
              const translateY = (1 - wordProgress) * 4
              const scale = 0.97 + wordProgress * 0.03

              return (
                <span
                  key={idx}
                  className="inline-block mr-[0.35em] transition-all duration-500 ease-out will-change-transform"
                  style={{
                    color: `rgba(27, 28, 30, ${opacity})`,
                    transform: `translateY(${translateY}px) scale(${scale})`,
                    fontWeight: wordProgress > 0.5 ? 600 : 400,
                  }}
                >
                  {word}
                </span>
              )
            })}
          </h2>
        </section>

        {/* ========================================== */}
        {/* 2. AGROVIA SMART SOLUTIONS ACCORDION       */}
        {/* ========================================== */}
        <section id="solutions" className="py-20 px-6 md:px-12 max-w-7xl mx-auto border-t border-black/5">
          
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-bold text-[#2E7D32] uppercase tracking-widest bg-[#2E7D32]/10 px-4 py-1.5 rounded-full">
              Innovative Architecture
            </span>
            <h2 className="font-serif-display text-3xl md:text-5xl font-normal text-[#1B1C1E] tracking-tight mt-4 mb-4">
              Smart Farming Solutions That <br /> Deliver Real Results
            </h2>
            <p className="text-sm md:text-base text-[#1B1C1E]/70 max-w-2xl mx-auto leading-relaxed">
              Experience the power of deterministic physics simulation and autonomous reasoning tailored to scale your agricultural productivity safely.
            </p>
          </div>

          {/* Grid Layout: Left Accordion List, Right Dynamic Media Preview */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
            
            {/* Left Accordion Menu */}
            <div className="lg:col-span-6 flex flex-col justify-center gap-4">
              {featureAccordionItems.map((item) => {
                const isOpen = activeAccordion === item.id
                return (
                  <div
                    key={item.id}
                    onClick={() => toggleAccordion(item.id)}
                    className={`cursor-pointer transition-all duration-300 ease-out rounded-2xl p-5 ${
                      isOpen
                        ? "bg-white shadow-xl ring-2 ring-[#2E7D32]/40 border-l-4 border-l-[#2E7D32] scale-[1.01]"
                        : "bg-white/60 hover:bg-white hover:shadow-md opacity-85"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <span className={`w-8 h-8 rounded-full flex items-center justify-center font-mono text-xs font-bold transition-all duration-300 ${
                          isOpen
                            ? "bg-[#2E7D32] text-white shadow-md scale-110"
                            : "bg-[#F3F5F3] text-[#1B1C1E]/60"
                        }`}>
                          0{item.id + 1}
                        </span>
                        <div>
                          <h3 className={`font-serif-display text-lg md:text-xl font-semibold transition-colors duration-300 ${
                            isOpen ? "text-[#2E7D32]" : "text-[#1B1C1E]"
                          }`}>
                            {item.title}
                          </h3>
                          <span className="text-xs font-semibold text-[#2E7D32]">
                            {item.tagline}
                          </span>
                        </div>
                      </div>
                      <div className={`p-1.5 rounded-full transition-all duration-300 ${isOpen ? "bg-[#2E7D32]/10 text-[#2E7D32] rotate-180" : "text-[#1B1C1E]/40"}`}>
                        <ChevronDown className="w-4 h-4" />
                      </div>
                    </div>

                    {/* Expanded Content with Grid Animation */}
                    <div className={`grid transition-all duration-500 ease-in-out ${isOpen ? "grid-rows-[1fr] opacity-100 mt-3 pt-3 border-t border-black/5" : "grid-rows-[0fr] opacity-0"}`}>
                      <div className="overflow-hidden">
                        <p className="text-xs md:text-sm text-[#1B1C1E]/70 leading-relaxed mb-3">
                          {item.desc}
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {item.metrics.map((m, mIdx) => (
                            <span key={mIdx} className="inline-flex items-center gap-1 bg-[#F3F5F3] text-[#2E7D32] text-[11px] font-semibold px-2.5 py-0.5 rounded-full border border-black/5">
                              <CheckCircle2 className="w-3 h-3 text-[#2E7D32]" />
                              <span>{m}</span>
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Right Media Preview Card */}
            <div className="lg:col-span-6 relative min-h-[440px] rounded-3xl overflow-hidden shadow-2xl group border border-black/10">
              {featureAccordionItems.map((item, idx) => (
                <img
                  key={item.id}
                  src={item.image}
                  alt={item.title}
                  className={`absolute inset-0 w-full h-full object-cover transition-all duration-700 ease-out ${
                    activeAccordion === idx ? "opacity-100 scale-100 z-10" : "opacity-0 scale-105 z-0"
                  }`}
                />
              ))}
              <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/25 to-transparent z-20" />
              
              {/* Media Overlay Badge */}
              <div className="absolute bottom-6 left-6 right-6 glass-card-dark p-5 rounded-2xl text-white shadow-2xl z-30 transition-transform duration-300 hover:scale-[1.02]">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-mono uppercase tracking-widest text-[#81C784]">
                    Feature Preview #{activeAccordion + 1}
                  </span>
                  <span className="w-2.5 h-2.5 rounded-full bg-[#4CAF50] animate-ping" />
                </div>
                <h4 className="font-serif-display text-xl font-normal mb-1.5 text-white">
                  {featureAccordionItems[activeAccordion].title}
                </h4>
                <p className="text-xs text-white/70 line-clamp-2">
                  {featureAccordionItems[activeAccordion].desc}
                </p>
              </div>
            </div>

          </div>

          {/* Step Controller Dots */}
          <div className="flex items-center justify-center gap-3 mt-8">
            {featureAccordionItems.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setActiveAccordion(idx)}
                className={`h-2.5 rounded-full transition-all duration-500 ${
                  activeAccordion === idx ? "w-10 bg-[#2E7D32]" : "w-2.5 bg-black/20 hover:bg-black/40"
                }`}
                aria-label={`Go to feature ${idx + 1}`}
              />
            ))}
          </div>

        </section>

        {/* ========================================== */}
        {/* 3. INTERACTIVE DASHBOARD FEATURE SHOWCASE  */}
        {/* ========================================== */}
        <section id="showcase" className="py-12 md:py-16 bg-[#F5FAF6] px-6 md:px-12 border-y border-black/5 overflow-hidden">
          <div className="max-w-7xl mx-auto space-y-6 md:space-y-8">
            
            {/* Header Layout (Matching Reference Picture 2) */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
              <div className="space-y-2.5 max-w-2xl">
                <div className="inline-flex items-center gap-2 bg-white px-3 py-1 rounded-full border border-black/5 shadow-sm text-xs font-semibold text-[#1B1C1E]">
                  <span className="w-2 h-2 rounded-full bg-[#2E7D32]" />
                  <span>How It Works</span>
                </div>
                <h2 className="font-sans text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold text-[#063B22] tracking-tight leading-[1.15]">
                  Smart Farming Made <br />
                  <span className="font-serif-display italic font-normal text-[#063B22]">Simple and Efficient</span>
                </h2>
              </div>
              <p className="text-sm md:text-base text-[#1B1C1E]/70 max-w-md leading-relaxed pb-1">
                A smart farming platform that connects soil, crops, and operations to help farmers grow more efficiently and safely.
              </p>
            </div>

            {/* Feature Tab Selectors Bar (4 cards matching Reference Picture 2) */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
              {[
                {
                  id: "overview",
                  title: "Overview",
                  subtitle: "Real-Time Insights",
                  icon: Calendar,
                },
                {
                  id: "planning",
                  title: "Smart Planning",
                  subtitle: "Precision Planning",
                  icon: Layers,
                },
                {
                  id: "control",
                  title: "Farm Control",
                  subtitle: "Total Management",
                  icon: Sliders,
                },
                {
                  id: "monitor",
                  title: "Field Monitor",
                  subtitle: "Growth Tracker",
                  icon: Sprout,
                },
              ].map((tab) => {
                const IconComponent = tab.icon
                const isActive = activeTab === tab.id
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-3.5 p-3.5 sm:p-4 rounded-2xl transition-all duration-300 text-left border ${
                      isActive
                        ? "bg-white shadow-lg border-black/10 scale-[1.01] ring-2 ring-[#2E7D32]/20"
                        : "bg-white/60 hover:bg-white hover:shadow-md border-black/5 opacity-80"
                    }`}
                  >
                    <div className={`p-2 rounded-xl shrink-0 transition-colors ${
                      isActive ? "bg-[#E8F5E9] text-[#2E7D32]" : "bg-[#F3F5F3] text-[#1B1C1E]/60"
                    }`}>
                      <IconComponent className="w-4 h-4 sm:w-5 sm:h-5" />
                    </div>
                    <div>
                      <div className="font-bold text-xs sm:text-sm text-[#1B1C1E]">{tab.title}</div>
                      <div className="text-[11px] text-[#1B1C1E]/60 font-medium">{tab.subtitle}</div>
                    </div>
                  </button>
                )
              })}
            </div>

            {/* Main Showcase Video Frame with Compact Height (Matching Uploaded Picture) */}
            <div className="relative w-full rounded-[2rem] sm:rounded-[2.5rem] overflow-hidden shadow-2xl border border-black/10 bg-slate-900 group aspect-[21/9] h-[340px] sm:h-[400px] md:h-[450px]">
              
              {/* Background Native MP4 Video Stream Layer */}
              <div className="absolute inset-0 z-0 overflow-hidden">
                <video
                  autoPlay
                  loop
                  muted
                  playsInline
                  poster="/agrovia-showcase-video.jpg"
                  className="w-full h-full object-cover transform origin-center scale-[1.02]"
                >
                  <source src="/gemini_generated_video_97dc7759.mp4" type="video/mp4" />
                </video>
                <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/15 to-black/20" />
              </div>

              {/* Bottom-Left Location Badge */}
              <div className="absolute bottom-4 left-4 sm:bottom-5 sm:left-5 z-20">
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-black/40 backdrop-blur-md border border-white/20 text-white text-[11px] sm:text-xs font-semibold shadow-lg">
                  <MapPin className="w-3.5 h-3.5 text-[#A3E635]" />
                  <span>Dhaka, Bangladesh</span>
                </div>
              </div>

              {/* Bottom-Right Floating Live Overlay Glass Cards (Matching Uploaded Reference Picture) */}
              <div className="absolute bottom-4 right-4 sm:bottom-5 sm:right-5 z-20 flex flex-col gap-2.5 max-w-[280px] sm:max-w-[300px] w-full">
                
                {/* Weather Glass Card */}
                <div className="bg-white/95 backdrop-blur-xl p-3 sm:p-4 rounded-2xl shadow-xl border border-white/50 text-[#1B1C1E] transition-all hover:scale-[1.01]">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2.5">
                      <div className="relative">
                        <Sun className="w-6 h-6 sm:w-7 sm:h-7 text-amber-400 fill-amber-400" />
                        <CloudRain className="w-4 h-4 text-blue-500 absolute -bottom-1 -right-1" />
                      </div>
                      <div>
                        <div className="text-xl sm:text-2xl font-extrabold text-[#1B1C1E] tracking-tight leading-none">24°C</div>
                        <div className="text-[10px] text-gray-500 font-medium">Today's Avg Temperature</div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-1.5 pt-2 border-t border-gray-100 text-center">
                    <div>
                      <div className="text-xs font-bold text-[#1B1C1E]">68%</div>
                      <div className="text-[9px] text-gray-400 font-medium">Humidity</div>
                    </div>
                    <div>
                      <div className="text-xs font-bold text-[#1B1C1E]">20%</div>
                      <div className="text-[9px] text-gray-400 font-medium">Precipitation</div>
                    </div>
                    <div>
                      <div className="text-xs font-bold text-[#1B1C1E]">12 km/h</div>
                      <div className="text-[9px] text-gray-400 font-medium">Wind Speed</div>
                    </div>
                  </div>
                </div>

                {/* Area Prediction AI Model Glass Card */}
                <div className="bg-white/95 backdrop-blur-xl p-3 sm:p-4 rounded-2xl shadow-xl border border-white/50 text-[#1B1C1E] transition-all hover:scale-[1.01]">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-[11px] font-bold text-[#1B1C1E]">Area Prediction AI Model</div>
                    <div className="inline-flex items-center gap-1 text-[9px] font-bold text-[#2E7D32] bg-[#E8F5E9] px-2 py-0.5 rounded-full">
                      <span>Good for planting</span>
                    </div>
                  </div>

                  {/* Bar chart score visualizer */}
                  <div className="h-5 flex items-end justify-between gap-1 my-2">
                    {[
                      "bg-red-400", "bg-red-400", "bg-orange-400", "bg-orange-400",
                      "bg-amber-400", "bg-amber-400", "bg-yellow-400", "bg-yellow-400",
                      "bg-lime-400", "bg-lime-400", "bg-emerald-400", "bg-emerald-400",
                      "bg-emerald-500", "bg-emerald-500", "bg-[#2E7D32]", "bg-[#2E7D32]",
                      "bg-[#2E7D32]", "bg-[#2E7D32]"
                    ].map((colorClass, idx) => (
                      <div
                        key={idx}
                        className={`flex-1 rounded-full ${colorClass} transition-all duration-300`}
                        style={{ height: `${40 + (idx % 6) * 10}%` }}
                      />
                    ))}
                  </div>

                  {/* Bottom AI callout banner */}
                  <div className="flex items-center justify-between bg-[#F3F5F3] p-1.5 rounded-xl text-xs">
                    <div className="flex items-center gap-1.5">
                      <span className="w-4 h-4 rounded-full bg-[#2E7D32] text-white flex items-center justify-center text-[9px] font-bold">AI</span>
                      <span className="font-semibold text-[10px] text-[#1B1C1E]">Farma AI helps optimize crop fields</span>
                    </div>
                    <ArrowRight className="w-3 h-3 text-[#1B1C1E]/60" />
                  </div>
                </div>

              </div>

            </div>

          </div>
        </section>

        {/* ========================================== */}
        {/* 4. METRICS & IMPACT GRID SECTION           */}
        {/* ========================================== */}
        <section id="metrics" className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
          
          {/* Section Header */}
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold text-[#2E7D32] uppercase tracking-widest bg-[#2E7D32]/10 px-4 py-1.5 rounded-full">
              Proven Impact
            </span>
            <h2 className="font-serif-display text-3xl md:text-5xl font-normal text-[#1B1C1E] tracking-tight mt-4">
              Empowering Agricultural Excellence
            </h2>
          </div>

          {/* 4-Column Numeric Stat Counters */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
            {[
              { stat: "1.5M+", label: "Acres Monitored", desc: "Across 14 global regions" },
              { stat: "200+", label: "Farmers Empowered", desc: "High-density polyhouse operations" },
              { stat: "2M+", label: "Decisions Optimized", desc: "Deterministic safety verified" },
              { stat: "750K+", label: "Successful Harvests", desc: "Zero crop loss record" },
            ].map((s, i) => (
              <div
                key={i}
                className="bg-white p-8 rounded-3xl shadow-sm border border-black/5 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 text-center group"
              >
                <span className="font-serif-display text-4xl lg:text-5xl font-bold text-[#2E7D32] block mb-2 group-hover:scale-110 transition-transform">
                  {s.stat}
                </span>
                <h4 className="font-bold text-[#1B1C1E] text-sm mb-1">{s.label}</h4>
                <p className="text-xs text-[#1B1C1E]/50">{s.desc}</p>
              </div>
            ))}
          </div>

          {/* Core Capabilities Card Carousel / Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: "Precision Crop Management",
                desc: "Real-time state estimation for physiological crop development.",
                image: "/agrovia-crop.jpg",
              },
              {
                title: "Smart Farm Automation",
                desc: "Autonomous edge drone & actuator dispatch routines.",
                image: "/agrovia-drone.jpg",
              },
              {
                title: "Sustainable Agriculture",
                desc: "Closed-loop hydroponic resource conservation.",
                image: "/agrovia-hero.jpg",
              },
              {
                title: "AI Crop Health Monitoring",
                desc: "Early biological anomaly detection and stress prevention.",
                image: "/agrovia-water.jpg",
              },
            ].map((card, i) => (
              <div
                key={i}
                className="group relative rounded-3xl overflow-hidden shadow-lg border border-black/5 h-[360px] flex flex-col justify-end p-6 cursor-pointer"
              >
                <img
                  src={card.image}
                  alt={card.title}
                  className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/30 to-transparent" />
                <div className="relative z-10 text-white">
                  <div className="w-8 h-8 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center mb-3 group-hover:bg-[#4CAF50] transition-colors">
                    <ArrowUpRight className="w-4 h-4 text-white group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                  </div>
                  <h3 className="font-serif-display text-xl font-semibold mb-2">
                    {card.title}
                  </h3>
                  <p className="text-xs text-white/70 line-clamp-2">
                    {card.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>

        </section>

        {/* ========================================== */}
        {/* 5. INTERACTIVE FAQ ACCORDION & FOOTER      */}
        {/* ========================================== */}
        <section id="faq" className="py-24 bg-[#F0F4F0] px-6 md:px-12 border-t border-black/5">
          <div className="max-w-4xl mx-auto">
            
            <div className="text-center mb-16">
              <span className="text-xs font-bold text-[#2E7D32] uppercase tracking-widest bg-white px-4 py-1.5 rounded-full shadow-sm">
                Got Questions?
              </span>
              <h2 className="font-serif-display text-3xl md:text-5xl font-normal text-[#1B1C1E] tracking-tight mt-4">
                Frequently Asked Questions
              </h2>
            </div>

            {/* Expandable FAQ Cards */}
            <div className="space-y-4">
              {faqs.map((faq, i) => {
                const isOpen = openFaq === i
                return (
                  <div
                    key={i}
                    onClick={() => setOpenFaq(isOpen ? null : i)}
                    className="bg-white rounded-2xl p-6 shadow-sm border border-black/5 cursor-pointer hover:shadow-md transition-all duration-300"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <h3 className="font-semibold text-base text-[#1B1C1E]">
                        {faq.q}
                      </h3>
                      <div className={`p-2 rounded-full transition-all duration-300 ${isOpen ? "bg-[#2E7D32] text-white rotate-180" : "bg-[#F3F5F3] text-[#1B1C1E]/60"}`}>
                        <ChevronDown className="w-4 h-4" />
                      </div>
                    </div>
                    {isOpen && (
                      <p className="mt-4 pt-4 border-t border-black/5 text-sm text-[#1B1C1E]/70 leading-relaxed animate-fadeIn">
                        {faq.a}
                      </p>
                    )}
                  </div>
                )
              })}
            </div>

          </div>
        </section>

        {/* Full-Width Hero Footer Banner */}
        <footer className="bg-[#1B1C1E] text-white pt-24 pb-12 px-6 md:px-12 relative overflow-hidden">
          
          <div className="max-w-7xl mx-auto">
            
            {/* Centralized CTA Banner */}
            <div className="text-center max-w-3xl mx-auto mb-20 pb-20 border-b border-white/10">
              <span className="text-xs font-bold text-[#A3E635] uppercase tracking-widest bg-white/10 px-4 py-1.5 rounded-full">
                Get Started Today
              </span>
              <h2 className="font-serif-display text-4xl md:text-6xl font-normal tracking-tight mt-6 mb-8 text-white">
                Make farming smarter, stronger, and simpler.
              </h2>
              <div className="flex flex-wrap justify-center items-center gap-4">
                <Link
                  href="/register"
                  className="bg-[#A3E635] hover:bg-[#86efac] text-black font-bold text-sm px-8 py-4 rounded-full shadow-lg transition-all hover:scale-105"
                >
                  Start Free Trial →
                </Link>
                <Link
                  href="#contact"
                  className="border border-white/40 hover:border-white bg-white/10 text-white font-semibold text-sm px-8 py-4 rounded-full transition-all"
                >
                  Schedule Demo
                </Link>
              </div>
            </div>

            {/* Sitemap Grid */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-16 text-sm">
              
              <div className="col-span-2">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 rounded-xl bg-[#A3E635] flex items-center justify-center text-black font-bold">
                    <Sprout className="w-4 h-4 text-black" />
                  </div>
                  <span className="font-sans font-bold text-xl text-white">
                    Agrovia <span className="text-[#A3E635] font-mono text-xs uppercase">Physica</span>
                  </span>
                </div>
                <p className="text-xs text-white/60 leading-relaxed max-w-sm mb-4">
                  The Physical Reality Compiler connecting natural language human intent to safe, deterministic polyhouse microclimate automation.
                </p>
                <div className="text-xs text-white/40 font-mono">
                  Repository: Santhosh-dev-lab/First-Commit
                </div>
              </div>

              <div>
                <h4 className="font-bold text-white mb-4 text-xs uppercase tracking-wider">Solutions</h4>
                <ul className="space-y-2.5 text-xs text-white/60">
                  <li><a href="#" className="hover:text-white transition-colors">Dwarf Tomato Optimizers</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Micro-Drip Irrigation</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">PAR Lighting Control</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Edge Gateway Bridge</a></li>
                </ul>
              </div>

              <div>
                <h4 className="font-bold text-white mb-4 text-xs uppercase tracking-wider">Company</h4>
                <ul className="space-y-2.5 text-xs text-white/60">
                  <li><a href="#" className="hover:text-white transition-colors">About Agrovia</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Research Papers</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Investor Relations</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                </ul>
              </div>

              <div>
                <h4 className="font-bold text-white mb-4 text-xs uppercase tracking-wider">Legal & Security</h4>
                <ul className="space-y-2.5 text-xs text-white/60">
                  <li><a href="#" className="hover:text-white transition-colors">Safety Verification Protocol</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Security Boundary</a></li>
                </ul>
              </div>

            </div>

            {/* Bottom Copyright */}
            <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row items-center justify-between text-xs text-white/40 gap-4">
              <span>© {new Date().getFullYear()} Agrovia PHYSICA Platform. All rights reserved.</span>
              <div className="flex gap-6">
                <a href="#" className="hover:text-white transition-colors">Twitter / X</a>
                <a href="#" className="hover:text-white transition-colors">GitHub</a>
                <a href="#" className="hover:text-white transition-colors">LinkedIn</a>
              </div>
            </div>

          </div>

        </footer>

      </main>

    </div>
  )
}
