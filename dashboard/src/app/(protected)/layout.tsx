"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    // Check authentication
    const checkAuth = async () => {
      try {
        // Let's actually use a simpler approach for the local demo: 
        // We'll call /api/auth/me with credentials
        const authRes = await fetch("/api/auth/me")
        
        if (!authRes.ok) {
          setIsAuthenticated(false)
          router.push("/login")
          return
        }
        
        // Check onboarding status
        const onboardingRes = await fetch("/api/onboarding/status")
        
        if (onboardingRes.ok) {
          const status = await onboardingRes.json()
          if (!status.completed) {
            router.push("/onboarding")
            return
          }
        }
        
        setIsAuthenticated(true)
      } catch (e) {
        setIsAuthenticated(false)
        router.push("/login")
      }
    }
    
    checkAuth()
  }, [router])

  if (isAuthenticated === null) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-[#050505] text-white">
        <div className="animate-pulse">Loading PHYSICA...</div>
      </div>
    )
  }

  if (isAuthenticated === false) {
    return null
  }

  return <>{children}</>
}
