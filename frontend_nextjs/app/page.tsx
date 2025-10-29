"use client"
import Link from "next/link"
import type React from "react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import {
  ArrowRight,
  Mail,
  Calendar,
  Users,
  Sparkles,
  Shield,
  Zap,
  CheckCircle2,
  Building2,
  Phone,
  Clock,
  Target,
  MessageSquare,
  BarChart3,
} from "lucide-react"
import { useState, useEffect, useRef } from "react"

function useScrollAnimation() {
  const ref = useRef<HTMLDivElement>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      { threshold: 0.1, rootMargin: "50px" },
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [])

  return { ref, isVisible }
}

function useStaggeredAnimation(itemCount: number) {
  const ref = useRef<HTMLDivElement>(null)
  const [visibleItems, setVisibleItems] = useState<boolean[]>(new Array(itemCount).fill(false))
  const hasTriggered = useRef(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasTriggered.current) {
          hasTriggered.current = true
          for (let index = 0; index < itemCount; index++) {
            setTimeout(() => {
              setVisibleItems((prev) => {
                const newState = [...prev]
                newState[index] = true
                return newState
              })
            }, index * 120)
          }
        }
      },
      { threshold: 0.1, rootMargin: "50px" },
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [itemCount])

  return { ref, visibleItems }
}

function useMousePosition() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener("mousemove", handleMouseMove)
    return () => window.removeEventListener("mousemove", handleMouseMove)
  }, [])

  return mousePosition
}

export default function LandingPage() {
  const [scrollY, setScrollY] = useState(0)
  const mousePosition = useMousePosition()

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <div className="min-h-screen overflow-x-hidden">
      <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-7xl">
        <div className="glass-card rounded-3xl px-8 py-4 shadow-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-black text-foreground">AgentFlow</span>
            </div>
            <div className="hidden md:flex items-center gap-10">
              <Link
                href="#features"
                className="text-sm font-bold text-foreground/70 hover:text-primary transition-colors"
              >
                Features
              </Link>
              <Link
                href="#pricing"
                className="text-sm font-bold text-foreground/70 hover:text-primary transition-colors"
              >
                Pricing
              </Link>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/login">
                <Button variant="ghost" size="sm" className="font-bold">
                  Sign In
                </Button>
              </Link>
              <Link href="/signup">
                <Button size="sm" className="bg-primary hover:bg-primary/90 text-white font-bold shadow-lg px-6">
                  Get Started
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <HeroSection scrollY={scrollY} mousePosition={mousePosition} />

      <DashboardPreview />

      <FeaturesSection />

      <StatsSection />

      <PricingSection />

      <CTASection />

      <Footer />
    </div>
  )
}

function HeroSection({ scrollY, mousePosition }: { scrollY: number; mousePosition: { x: number; y: number } }) {
  const heroTextRef = useRef<HTMLHeadingElement>(null)
  const [textOffset, setTextOffset] = useState({ x: 0, y: 0 })

  useEffect(() => {
    if (!heroTextRef.current) return

    const centerX = window.innerWidth / 2
    const centerY = window.innerHeight / 2

    const offsetX = (mousePosition.x - centerX) / 50
    const offsetY = (mousePosition.y - centerY) / 50

    setTextOffset((prev) => ({
      x: prev.x + (offsetX - prev.x) * 0.1,
      y: prev.y + (offsetY - prev.y) * 0.1,
    }))
  }, [mousePosition])

  return (
    <section className="min-h-screen relative overflow-hidden flex items-center justify-center pt-32 pb-20 px-6">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute top-[10%] left-[5%] w-[600px] h-[600px] rounded-full blur-3xl opacity-40"
          style={{
            background: "radial-gradient(circle, rgba(0, 102, 255, 0.6), transparent 70%)",
            transform: `translate(${mousePosition.x * 0.02}px, ${mousePosition.y * 0.02 + scrollY * 0.3}px)`,
          }}
        />
        <div
          className="absolute top-[30%] right-[5%] w-[700px] h-[700px] rounded-full blur-3xl opacity-40"
          style={{
            background: "radial-gradient(circle, rgba(0, 212, 255, 0.5), transparent 70%)",
            transform: `translate(${-mousePosition.x * 0.03}px, ${-mousePosition.y * 0.03 + scrollY * 0.5}px)`,
          }}
        />
        <div
          className="absolute bottom-[10%] left-[20%] w-[500px] h-[500px] rounded-full blur-3xl opacity-30"
          style={{
            background: "radial-gradient(circle, rgba(255, 107, 107, 0.5), transparent 70%)",
            transform: `translate(${mousePosition.x * 0.015}px, ${mousePosition.y * 0.015 + scrollY * 0.4}px)`,
          }}
        />
      </div>

      <div className="container mx-auto max-w-7xl relative z-10">
        <div className="text-center space-y-12">
          <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full glass-card text-sm font-bold shadow-xl animate-fade-in-up">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-primary"></span>
            </span>
            <span className="text-foreground">Trusted by 500+ top-producing agents</span>
          </div>

          <h1
            ref={heroTextRef}
            className="text-7xl sm:text-8xl md:text-9xl lg:text-[11rem] font-black text-balance leading-[0.85] tracking-tighter animate-fade-in-up text-white"
            style={{
              animationDelay: "0.1s",
              opacity: 0,
              animationFillMode: "forwards",
              transform: `translate(${textOffset.x}px, ${textOffset.y}px)`,
              transition: "transform 0.3s ease-out",
              textShadow: "0 4px 20px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 102, 255, 0.4)",
            }}
          >
            Your Command
            <br />
            Center for
            <br />
            Real Estate
          </h1>

          <p
            className="text-2xl md:text-3xl text-white/90 max-w-4xl mx-auto text-balance leading-relaxed font-semibold animate-fade-in-up"
            style={{ animationDelay: "0.2s", opacity: 0, animationFillMode: "forwards" }}
          >
            Transform chaos into calm with intelligent automation, unified communications, and AI-powered insights
          </p>

          <div
            className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-12 animate-fade-in-up"
            style={{ animationDelay: "0.3s", opacity: 0, animationFillMode: "forwards" }}
          >
            <Link href="/signup">
              <Button
                size="lg"
                className="bg-gradient-to-r from-primary to-secondary hover:shadow-2xl hover:scale-105 text-white text-xl px-16 h-20 font-black shadow-2xl rounded-2xl transition-all duration-300"
              >
                Start Free Trial
                <ArrowRight className="ml-4 w-7 h-7" />
              </Button>
            </Link>
            <Button
              size="lg"
              variant="outline"
              className="text-xl px-16 h-20 font-black glass-card border-2 hover:border-primary bg-transparent rounded-2xl hover:scale-105 transition-all duration-300"
            >
              Watch Demo
            </Button>
          </div>

          <div
            className="flex items-center justify-center gap-12 pt-12 text-base font-bold text-foreground/60 animate-fade-in-up"
            style={{ animationDelay: "0.4s", opacity: 0, animationFillMode: "forwards" }}
          >
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-primary" />
              No credit card
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-primary" />
              14-day trial
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-primary" />
              Cancel anytime
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function DashboardPreview() {
  const { ref, isVisible } = useScrollAnimation()
  const cardRef = useRef<HTMLDivElement>(null)

  return (
    <section ref={ref} className="py-32 px-6 relative main-bg">
      <div className="container mx-auto max-w-7xl">
        <div className="text-center space-y-8 mb-20">
          <h2
            className={`text-6xl md:text-7xl font-black text-balance leading-tight text-foreground transition-all duration-1000 ${
              isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
            }`}
          >
            See your entire business at a glance
          </h2>
          <p
            className={`text-2xl text-foreground/70 max-w-3xl mx-auto font-semibold transition-all duration-1000 delay-100 ${
              isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
            }`}
          >
            Beautiful, data-rich interface designed for clarity and speed
          </p>
        </div>

        <div
          ref={cardRef}
          className={`max-w-6xl mx-auto transition-all duration-1000 delay-200 ${
            isVisible ? "opacity-100 scale-100" : "opacity-0 scale-95"
          }`}
        >
          <Card className="glass-card p-12 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-10">
                <h3 className="text-4xl font-black text-foreground">Unified Timeline</h3>
                <div className="flex items-center gap-3 text-base font-bold text-primary">
                  <div className="w-3 h-3 rounded-full bg-primary animate-pulse" />
                  Live Updates
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                {[
                  {
                    icon: Mail,
                    name: "Sarah Johnson",
                    time: "2m ago",
                    message: "Interested in viewing the luxury condo this weekend",
                    type: "Email",
                    color: "from-blue-500 to-cyan-500",
                  },
                  {
                    icon: Phone,
                    name: "Mike Chen",
                    time: "15m ago",
                    message: "Called about the downtown listing",
                    type: "Call",
                    color: "from-purple-500 to-pink-500",
                  },
                  {
                    icon: Calendar,
                    name: "Emma Davis",
                    time: "1h ago",
                    message: "Confirmed showing appointment for tomorrow",
                    type: "Meeting",
                    color: "from-orange-500 to-red-500",
                  },
                  {
                    icon: MessageSquare,
                    name: "John Smith",
                    time: "2h ago",
                    message: "Sent offer documents for review",
                    type: "Message",
                    color: "from-green-500 to-teal-500",
                  },
                ].map((item, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-5 p-6 rounded-3xl bg-white/80 dark:bg-white/5 backdrop-blur-sm border-2 border-border hover:border-primary/50 transition-all duration-500 hover:scale-105 hover:shadow-xl"
                  >
                    <div
                      className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${item.color} flex items-center justify-center flex-shrink-0 shadow-lg`}
                    >
                      <item.icon className="w-7 h-7 text-white" />
                    </div>
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center justify-between">
                        <p className="font-black text-lg text-foreground">{item.name}</p>
                        <span className="text-sm font-bold text-muted-foreground">{item.time}</span>
                      </div>
                      <p className="text-base text-foreground/70 leading-relaxed font-medium">{item.message}</p>
                      <span className="inline-block px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold">
                        {item.type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </section>
  )
}

function FeaturesSection() {
  const { ref, visibleItems } = useStaggeredAnimation(6)

  const features = [
    {
      icon: Sparkles,
      title: "AI-Powered Triage",
      description: "Claude AI automatically flags urgent emails, summarizes threads, and drafts personalized responses",
      span: "col-span-12 md:col-span-8 row-span-1",
      gradient: "from-blue-500/10 to-cyan-500/10",
    },
    {
      icon: Mail,
      title: "Unified Timeline",
      description: "Every email, call, text, and note in one beautiful chronological view",
      span: "col-span-12 md:col-span-4 row-span-2",
      gradient: "from-purple-500/10 to-pink-500/10",
    },
    {
      icon: Calendar,
      title: "Smart Automation",
      description: "Automatically convert emails into tasks and calendar events",
      span: "col-span-12 md:col-span-4 row-span-1",
      gradient: "from-orange-500/10 to-red-500/10",
    },
    {
      icon: Shield,
      title: "Trustworthy AI",
      description: "AI suggests, you approve. Human-in-the-loop design means you're always in control",
      span: "col-span-12 md:col-span-4 row-span-1",
      gradient: "from-green-500/10 to-teal-500/10",
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Timeline loads in under 500ms. No more waiting for clunky software",
      span: "col-span-12 md:col-span-5 row-span-1",
      gradient: "from-yellow-500/10 to-orange-500/10",
    },
    {
      icon: BarChart3,
      title: "Advanced Analytics",
      description: "Track response times, conversion rates, and client engagement metrics",
      span: "col-span-12 md:col-span-7 row-span-1",
      gradient: "from-indigo-500/10 to-purple-500/10",
    },
  ]

  return (
    <section id="features" ref={ref} className="py-32 px-6 relative main-bg">
      <div className="container mx-auto max-w-7xl">
        <div className="text-center space-y-8 mb-24">
          <h2 className="text-6xl md:text-8xl font-black text-balance leading-tight text-foreground">
            Everything you need to dominate
          </h2>
          <p className="text-2xl text-foreground/70 max-w-3xl mx-auto text-balance font-semibold">
            Built for agents who refuse to let opportunities slip away
          </p>
        </div>

        <div className="grid grid-cols-12 auto-rows-[280px] gap-6">
          {features.map((feature, i) => (
            <Card
              key={i}
              className={`${feature.span} glass-card p-10 relative overflow-hidden group transition-all duration-700 hover:scale-[1.02] hover:shadow-2xl ${
                visibleItems[i] ? "opacity-100 scale-100" : "opacity-0 scale-90"
              }`}
              style={{ transitionDelay: `${i * 50}ms` }}
            >
              <div
                className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
              />
              <div className="relative z-10 h-full flex flex-col">
                <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mb-8 shadow-2xl group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                  <feature.icon className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-3xl font-black text-foreground mb-5">{feature.title}</h3>
                <p className="text-lg text-foreground/70 leading-relaxed font-semibold">{feature.description}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

function StatsSection() {
  const { ref, isVisible } = useScrollAnimation()
  const [counts, setCounts] = useState([0, 0, 0, 0])

  useEffect(() => {
    if (!isVisible) return

    const targets = [500, 5, 98, 24]
    const duration = 2000
    const steps = 60
    const increment = targets.map((target) => target / steps)

    let currentStep = 0
    const timer = setInterval(() => {
      currentStep++
      setCounts(targets.map((target, i) => Math.min(Math.floor(increment[i] * currentStep), target)))

      if (currentStep >= steps) {
        clearInterval(timer)
        setCounts(targets)
      }
    }, duration / steps)

    return () => clearInterval(timer)
  }, [isVisible])

  const stats = [
    { value: counts[0], suffix: "+", label: "Active Agents", icon: Users },
    { value: counts[1], suffix: "hrs", label: "Saved Per Week", icon: Clock },
    { value: counts[2], suffix: "%", label: "Satisfaction Rate", icon: Target },
    { value: counts[3], suffix: "/7", label: "AI Assistant", icon: Sparkles },
  ]

  return (
    <section ref={ref} className="py-32 px-6 relative main-bg">
      <div className="container mx-auto max-w-7xl">
        <div className="grid md:grid-cols-4 gap-12">
          {stats.map((stat, i) => (
            <div
              key={i}
              className={`text-center space-y-6 transition-all duration-1000 ${
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
              }`}
              style={{ transitionDelay: `${i * 100}ms` }}
            >
              <div className="w-24 h-24 rounded-[2rem] bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto shadow-2xl hover:scale-110 transition-transform duration-300">
                <stat.icon className="w-12 h-12 text-white" />
              </div>
              <div className="text-7xl font-black bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                {stat.value}
                {stat.suffix}
              </div>
              <div className="text-lg font-black text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function PricingSection() {
  const { ref, visibleItems } = useStaggeredAnimation(3)
  const [hoveredCard, setHoveredCard] = useState<number | null>(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>, index: number) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left - rect.width / 2
    const y = e.clientY - rect.top - rect.height / 2
    setMousePos({ x: x / 20, y: y / 20 })
    setHoveredCard(index)
  }

  const handleMouseLeave = () => {
    setHoveredCard(null)
    setMousePos({ x: 0, y: 0 })
  }

  const plans = [
    {
      name: "Solo Agent",
      price: "$39",
      description: "Perfect for individual agents",
      features: ["Unlimited contacts", "Email integration", "AI-powered triage", "Unified timeline", "Mobile app"],
      cta: "Start Free Trial",
      popular: false,
    },
    {
      name: "Pro Agent",
      price: "$99",
      description: "For top producers",
      features: [
        "Everything in Solo",
        "Transaction management",
        "MLS integration",
        "Advanced analytics",
        "Priority support",
        "Custom workflows",
      ],
      cta: "Start Free Trial",
      popular: true,
    },
    {
      name: "Team",
      price: "$199",
      description: "+ $49 per additional user",
      features: [
        "Everything in Pro",
        "Team collaboration",
        "Shared dashboards",
        "Admin controls",
        "Dedicated support",
        "Custom integrations",
      ],
      cta: "Contact Sales",
      popular: false,
    },
  ]

  return (
    <section id="pricing" ref={ref} className="py-32 px-6 main-bg">
      <div className="container mx-auto max-w-7xl">
        <div className="text-center space-y-8 mb-24">
          <h2 className="text-6xl md:text-8xl font-black text-foreground">Choose your plan</h2>
          <p className="text-2xl text-foreground/70 max-w-3xl mx-auto font-semibold">
            Start free, scale as you grow. No hidden fees.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, i) => (
            <div
              key={i}
              className={`relative transition-all duration-700 ${
                visibleItems[i] ? "opacity-100 scale-100" : "opacity-0 scale-90"
              }`}
              onMouseMove={(e) => handleMouseMove(e, i)}
              onMouseLeave={handleMouseLeave}
              style={{
                transform: hoveredCard === i ? `translate(${mousePos.x}px, ${mousePos.y}px)` : "translate(0px, 0px)",
                transition: hoveredCard === i ? "transform 0.1s ease-out" : "transform 0.3s ease-out",
              }}
            >
              {plan.popular && (
                <div className="absolute -top-5 left-1/2 -translate-x-1/2 z-20 px-8 py-3 bg-gradient-to-r from-primary to-secondary text-white text-sm font-black rounded-full shadow-xl">
                  MOST POPULAR
                </div>
              )}
              <Card
                className={`bg-white dark:bg-white/95 backdrop-blur-xl p-10 space-y-8 relative overflow-hidden border-2 transition-all duration-500 h-full ${
                  plan.popular
                    ? "border-primary shadow-2xl shadow-primary/20 scale-[1.02]"
                    : "border-border/20 hover:border-primary/50"
                } ${hoveredCard === i ? "shadow-3xl scale-105" : ""}`}
              >
                {plan.popular && (
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5 pointer-events-none" />
                )}
                <div className="relative z-10 space-y-6">
                  <h3 className="text-3xl font-black text-gray-900">{plan.name}</h3>
                  <div className="flex items-baseline gap-2">
                    <span className="text-6xl font-black text-gray-900">{plan.price}</span>
                    <span className="text-gray-500 font-bold text-lg">/ month</span>
                  </div>
                  <p className="text-base text-gray-600 font-semibold">{plan.description}</p>
                </div>

                <div className="relative z-10 border-t border-gray-200 pt-8">
                  <ul className="space-y-5">
                    {plan.features.map((feature, j) => (
                      <li key={j} className="flex items-start gap-3">
                        <CheckCircle2 className="w-6 h-6 text-primary flex-shrink-0 mt-0.5" />
                        <span className="text-base font-semibold text-gray-700 leading-relaxed">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <Button
                  className={`relative z-10 w-full h-14 font-black text-base rounded-xl shadow-lg hover:shadow-xl transition-all hover:scale-105 ${
                    plan.popular
                      ? "bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-white"
                      : "bg-gray-900 hover:bg-gray-800 text-white"
                  }`}
                >
                  {plan.cta}
                </Button>
              </Card>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function CTASection() {
  const { ref, isVisible } = useScrollAnimation()

  return (
    <section ref={ref} className="py-40 px-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-secondary/20 to-accent/20" />
      <div className="container mx-auto max-w-6xl relative z-10">
        <Card
          className={`glass-card p-20 text-center space-y-12 relative overflow-hidden transition-all duration-1000 ${
            isVisible ? "opacity-100 scale-100" : "opacity-0 scale-95"
          }`}
        >
          <div className="relative z-10">
            <h2 className="text-6xl md:text-8xl font-black text-balance mb-10 leading-tight text-foreground">
              Ready to transform your workflow?
            </h2>
            <p className="text-2xl text-foreground/70 max-w-3xl mx-auto mb-16 font-semibold">
              Join hundreds of agents who've already taken control of their business
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
              <Link href="/signup">
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-primary to-secondary hover:shadow-2xl hover:scale-105 text-white text-xl px-16 h-20 font-black shadow-2xl rounded-2xl transition-all duration-300"
                >
                  Start Your Free Trial
                  <ArrowRight className="ml-4 w-7 h-7" />
                </Button>
              </Link>
              <Button
                size="lg"
                variant="outline"
                className="text-xl px-16 h-20 font-black glass-card border-2 hover:border-primary bg-transparent rounded-2xl hover:scale-105 transition-all duration-300"
              >
                Schedule a Demo
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="border-t border-border/40 py-24 px-6 relative main-bg">
      <div className="container mx-auto max-w-7xl">
        <div className="grid md:grid-cols-5 gap-16 mb-20">
          <div className="md:col-span-2 space-y-8">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-3xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-xl">
                <Building2 className="w-8 h-8 text-white" />
              </div>
              <span className="text-4xl font-black text-foreground">AgentFlow</span>
            </div>
            <p className="text-foreground/70 leading-relaxed max-w-md font-semibold text-lg">
              The intelligent command center for modern real estate agents. Transform chaos into calm with AI-powered
              automation.
            </p>
          </div>
          <div className="space-y-6">
            <h4 className="font-black text-base uppercase tracking-wider text-foreground">Product</h4>
            <ul className="space-y-4 text-base text-muted-foreground font-bold">
              {["Features", "Pricing", "Integrations", "Changelog"].map((item, i) => (
                <li key={i}>
                  <Link href="#" className="hover:text-primary transition-colors">
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div className="space-y-6">
            <h4 className="font-black text-base uppercase tracking-wider text-foreground">Company</h4>
            <ul className="space-y-4 text-base text-muted-foreground font-bold">
              {["About", "Blog", "Careers", "Contact"].map((item, i) => (
                <li key={i}>
                  <Link href="#" className="hover:text-primary transition-colors">
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div className="space-y-6">
            <h4 className="font-black text-base uppercase tracking-wider text-foreground">Legal</h4>
            <ul className="space-y-4 text-base text-muted-foreground font-bold">
              {["Privacy", "Terms", "Security"].map((item, i) => (
                <li key={i}>
                  <Link href="#" className="hover:text-primary transition-colors">
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="pt-12 border-t border-border/40 flex flex-col md:flex-row items-center justify-between gap-6">
          <p className="text-base text-muted-foreground font-bold">© 2025 AgentFlow. All rights reserved.</p>
          <div className="flex items-center gap-10 text-base text-muted-foreground font-bold">
            <Link href="#" className="hover:text-primary transition-colors">
              Twitter
            </Link>
            <Link href="#" className="hover:text-primary transition-colors">
              LinkedIn
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
