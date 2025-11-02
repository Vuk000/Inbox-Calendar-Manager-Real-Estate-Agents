'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { 
  Mail, Calendar, BarChart3, Shield, Zap, Users, CheckCircle2, 
  Camera, MapPin, FileText, CheckSquare, User, Building2, Sparkles,
  MessageSquare, Clock, TrendingUp, Eye, Brain, Workflow, Lock,
  ArrowRight, Play, Star, Award, Target, Rocket
} from 'lucide-react';
import Link from 'next/link';
import { motion, useScroll, useTransform } from 'framer-motion';
import { TextReveal } from '@/components/TextReveal';
import { useRef } from 'react';

export default function LandingPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll();

  const coreFeatures = [
    {
      icon: Mail,
      title: 'Unified Inbox',
      description: 'Manage all your email accounts (Gmail, Outlook) in one centralized inbox. AI automatically triages, prioritizes, and organizes messages by urgency and type.',
      benefits: ['Multi-account support', 'Smart prioritization', 'Thread management', 'Real-time sync'],
    },
    {
      icon: Brain,
      title: 'AI Email Triage',
      description: 'Our advanced AI analyzes every email and automatically categorizes it as an offer, lead inquiry, inspection request, or general communication. Never miss a critical message again.',
      benefits: ['Instant categorization', 'Urgency scoring', 'Lead detection', 'Auto-prioritization'],
    },
    {
      icon: FileText,
      title: 'AI Draft Generation',
      description: 'Generate personalized email responses in your voice. AI creates multiple draft variations, learns your communication style, and ensures every response maintains your professional tone.',
      benefits: ['Multiple variants', 'Voice matching', 'Context-aware', 'One-click send'],
    },
    {
      icon: Calendar,
      title: 'Smart Calendar',
      description: 'AI suggests optimal meeting times based on your availability and preferences. Automatically convert emails to calendar events and manage your schedule intelligently.',
      benefits: ['Auto-scheduling', 'Conflict detection', 'Smart suggestions', 'Multi-calendar sync'],
    },
    {
      icon: CheckSquare,
      title: 'Task Automation',
      description: 'Turn emails into actionable tasks automatically. AI extracts action items, sets priorities, and creates follow-up reminders. Never drop the ball on client requests.',
      benefits: ['Auto-task creation', 'Priority detection', 'Deadline tracking', 'Kanban boards'],
    },
    {
      icon: BarChart3,
      title: 'Analytics & Insights',
      description: 'Track your productivity, email response times, lead conversion rates, and ROI. Get actionable insights to grow your business and improve client relationships.',
      benefits: ['Response time metrics', 'Lead conversion tracking', 'Productivity reports', 'ROI analysis'],
    },
    {
      icon: Camera,
      title: 'VisionHome AI',
      description: 'Scan property photos with computer vision technology. Get instant property analysis, renovation suggestions, and virtual staging recommendations powered by advanced AI.',
      benefits: ['Property analysis', 'Renovation ideas', 'Virtual staging', 'Market insights'],
    },
    {
      icon: MapPin,
      title: 'Neighborhood Whisper',
      description: 'AI-powered neighborhood fit scores and analysis. Get comprehensive reports on schools, demographics, market trends, and lifestyle fit for your clients.',
      benefits: ['Fit scoring', 'Market analysis', 'School ratings', 'Trend forecasting'],
    },
    {
      icon: User,
      title: 'Contact Management',
      description: 'Unified CRM with complete contact timelines. See every interaction across email, SMS, and social media. Automatic contact enrichment and relationship tracking.',
      benefits: ['Unified timeline', 'Contact enrichment', 'Relationship tracking', 'Deal pipeline'],
    },
    {
      icon: Building2,
      title: 'Transaction Pipeline',
      description: 'Manage your entire transaction lifecycle from offer to closing. Track deals, manage checklists, automate follow-ups, and never miss a critical deadline.',
      benefits: ['Deal tracking', 'Automated checklists', 'Deadline reminders', 'Commission tracking'],
    },
    {
      icon: Sparkles,
      title: 'AI Actions',
      description: 'Human-in-the-loop AI workflow. AI suggests actions like sending follow-ups, scheduling meetings, or updating contact info. You approve before execution.',
      benefits: ['Action suggestions', 'Human approval', 'Batch processing', 'Smart automation'],
    },
    {
      icon: Users,
      title: 'Team Collaboration',
      description: 'Work seamlessly with your team. Shared inboxes, team assignments, collaboration tools, and real-time updates. Perfect for brokerages and teams.',
      benefits: ['Shared inboxes', 'Team assignments', 'Real-time sync', 'Role management'],
    },
  ];

  const advancedFeatures = [
    {
      title: 'Lead Qualification',
      description: 'AI automatically scores and qualifies leads from email inquiries. Enrich contacts with property history, buying power analysis, and engagement scoring.',
      icon: Target,
    },
    {
      title: 'Voice Mode',
      description: 'Dictate emails and tasks using voice commands. Perfect for when you\'re on the go or between showings.',
      icon: MessageSquare,
    },
    {
      title: 'Integrations',
      description: 'Connect with Gmail, Outlook, Twilio SMS, WhatsApp, and more. All communications unified in one timeline.',
      icon: Workflow,
    },
    {
      title: 'Security',
      description: 'Enterprise-grade security with AES-256 encryption, RBAC, audit logs, and GDPR compliance. Your data is always protected.',
      icon: Lock,
    },
  ];

  const useCases = [
    {
      title: 'Lead Response Automation',
      description: 'Automatically detect new leads, generate personalized responses, and schedule follow-ups. Never let a lead go cold.',
      icon: Rocket,
    },
    {
      title: 'Offer Management',
      description: 'Instantly recognize offers, analyze terms, and generate counter-offer suggestions. Speed up your negotiation process.',
      icon: FileText,
    },
    {
      title: 'Client Communication',
      description: 'Maintain consistent communication with all clients. Auto-draft updates, schedule showings, and never miss a check-in.',
      icon: MessageSquare,
    },
    {
      title: 'Transaction Management',
      description: 'Track every transaction from offer to closing. Automated checklists, deadline reminders, and milestone tracking.',
      icon: CheckSquare,
    },
  ];

  const stats = [
    { value: '10+', label: 'Hours Saved Per Week', icon: Clock },
    { value: '73%', label: 'Faster Response Time', icon: Zap },
    { value: '500+', label: 'AI Actions Per Month', icon: Sparkles },
    { value: '99.9%', label: 'Uptime SLA', icon: Shield },
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Top Producer, Century 21',
      content: 'RealInbox AI transformed how I manage my business. I save 2 hours daily and never miss a lead.',
      rating: 5,
    },
    {
      name: 'Michael Chen',
      role: 'Team Lead, Keller Williams',
      content: 'The AI draft feature is incredible. It matches my voice perfectly and generates responses I\'d write myself.',
      rating: 5,
    },
    {
      name: 'Emily Rodriguez',
      role: 'Independent Agent',
      content: 'Finally, a tool that understands real estate. The transaction pipeline feature alone is worth the price.',
      rating: 5,
    },
  ];

  const pricingTiers = [
    {
      name: 'Solo Agent',
      price: '$29',
      period: '/month',
      description: 'Perfect for individual agents',
      features: [
        '1 email account',
        '500 AI actions/month',
        'Core features',
        'Email support',
      ],
      popular: false,
    },
    {
      name: 'Pro Agent',
      price: '$49',
      period: '/month',
      description: 'For power users and top producers',
      features: [
        '3 email accounts',
        'Unlimited AI actions',
        'Advanced analytics',
        'Voice mode',
        'Priority support',
      ],
      popular: true,
    },
    {
      name: 'Team',
      price: '$149',
      period: '/month',
      description: 'For teams and small brokerages',
      features: [
        '5 agents included',
        'Shared inboxes',
        'Team collaboration',
        'Admin dashboard',
        'Dedicated support',
      ],
      popular: false,
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  // Parallax transforms
  const heroY = useTransform(scrollYProgress, [0, 0.5], [0, -50]);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0]);

  return (
    <div className="min-h-screen bg-white relative overflow-hidden">
      {/* Subtle background gradient */}
      <div className="fixed inset-0 bg-gradient-to-b from-gray-50 via-white to-gray-50 pointer-events-none z-0"></div>
      
      {/* Header */}
      <motion.header 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6 }}
        className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm"
      >
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <motion.div 
              className="flex items-center gap-2"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-sm">
                <Mail className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-semibold text-gray-900">RealInbox AI Pro</span>
            </motion.div>
            <div className="flex items-center gap-4">
              {isAuthenticated ? (
                <Button onClick={() => router.push('/dashboard')} variant="default">
                  Go to Dashboard
                </Button>
              ) : (
                <>
                  <Link href="/signin">
                    <Button variant="ghost">Sign In</Button>
                  </Link>
                  <Link href="/signup">
                    <Button>Get Started</Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </motion.header>

      {/* Hero Section */}
      <section ref={heroRef} className="container mx-auto px-4 py-20 md:py-32 relative z-10">
        <motion.div 
          className="max-w-5xl mx-auto text-center"
          style={{ y: heroY, opacity: heroOpacity }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            className="mb-6"
          >
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium border border-blue-100">
              <Sparkles className="w-4 h-4" />
              Powered by Claude Sonnet 4.5 AI
            </span>
          </motion.div>
          
          <motion.h1 
            className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.8 }}
          >
            Stop Drowning in Email Chaos
            <span className="block text-blue-600 mt-4">
              Start Closing More Deals
            </span>
          </motion.h1>
          
          <TextReveal delay={0.4}>
            <p className="text-xl md:text-2xl text-gray-600 mb-4 max-w-3xl mx-auto font-medium">
              The all-in-one AI platform that automates your inbox, qualifies leads, drafts responses, 
              and manages your entire real estate business. Save 10+ hours per week.
            </p>
          </TextReveal>
          
          <TextReveal delay={0.6}>
            <p className="text-lg text-gray-500 mb-8 max-w-2xl mx-auto">
              Used by 500+ real estate professionals. Trusted by top producers and teams nationwide.
            </p>
          </TextReveal>
          
          <motion.div 
            className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.8 }}
          >
            {!isAuthenticated && (
              <>
                <Link href="/signup">
                  <Button size="lg" className="w-full sm:w-auto text-lg px-8 py-6 shadow-lg">
                    Start Free Trial
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                </Link>
                <Link href="/signin">
                  <Button size="lg" variant="outline" className="w-full sm:w-auto text-lg px-8 py-6">
                    Watch Demo
                    <Play className="ml-2 w-5 h-5" />
                  </Button>
                </Link>
              </>
            )}
          </motion.div>

          {/* Stats Bar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1, duration: 0.8 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto"
          >
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <Card key={index} className="p-6 bg-white border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-center mb-3">
                    <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                      <Icon className="w-5 h-5 text-blue-600" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                  <div className="text-sm text-gray-600">{stat.label}</div>
                </Card>
              );
            })}
          </motion.div>
        </motion.div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gray-50 relative z-10">
        <div className="container mx-auto px-4">
          <TextReveal>
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                How RealInbox AI Works
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Three simple steps to transform your business
              </p>
            </div>
          </TextReveal>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                step: '01',
                title: 'Connect Your Accounts',
                description: 'Securely connect your Gmail, Outlook, and other email accounts. Our AI starts analyzing immediately.',
                icon: Mail,
              },
              {
                step: '02',
                title: 'AI Takes Over',
                description: 'AI triages emails, generates drafts, qualifies leads, and suggests actions. You review and approve.',
                icon: Brain,
              },
              {
                step: '03',
                title: 'Close More Deals',
                description: 'Never miss a lead. Respond faster. Close more deals. Watch your productivity and revenue soar.',
                icon: TrendingUp,
              },
            ].map((step, index) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.2, duration: 0.6 }}
                  className="relative"
                >
                  <Card className="p-8 h-full bg-white border border-gray-200 shadow-sm hover:shadow-lg transition-shadow">
                    <div className="text-5xl font-bold text-blue-600 mb-4 opacity-20">{step.step}</div>
                    <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-3">{step.title}</h3>
                    <p className="text-gray-600">{step.description}</p>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Core Features Section */}
      <section className="py-20 bg-white relative z-10">
        <div className="container mx-auto px-4">
          <TextReveal>
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Everything You Need to Succeed
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                12 powerful features designed specifically for real estate professionals
              </p>
            </div>
          </TextReveal>
          
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {coreFeatures.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  variants={itemVariants}
                  whileHover={{ y: -5 }}
                  transition={{ duration: 0.2 }}
                >
                  <Card className="p-6 h-full bg-white border border-gray-200 shadow-sm hover:shadow-lg transition-all">
                    <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center mb-4">
                      <Icon className="w-6 h-6 text-blue-600" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">{feature.title}</h3>
                    <p className="text-gray-600 mb-4">{feature.description}</p>
                    <div className="space-y-2">
                      {feature.benefits.map((benefit, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
                          <CheckCircle2 className="w-4 h-4 text-blue-600 flex-shrink-0" />
                          <span>{benefit}</span>
                        </div>
                      ))}
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-20 bg-gray-50 relative z-10">
        <div className="container mx-auto px-4">
          <TextReveal>
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Real-World Use Cases
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                See how RealInbox AI solves real problems for real estate professionals
              </p>
            </div>
          </TextReveal>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {useCases.map((useCase, index) => {
              const Icon = useCase.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6 }}
                >
                  <Card className="p-8 bg-white border border-gray-200 shadow-sm hover:shadow-lg transition-shadow">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">{useCase.title}</h3>
                        <p className="text-gray-600">{useCase.description}</p>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Advanced Features Section */}
      <section className="py-20 bg-white relative z-10">
        <div className="container mx-auto px-4">
          <TextReveal>
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Enterprise-Grade Features
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Built for scale, security, and performance
              </p>
            </div>
          </TextReveal>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {advancedFeatures.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1, duration: 0.5 }}
                >
                  <Card className="p-6 text-center bg-white border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                    <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                    <p className="text-sm text-gray-600">{feature.description}</p>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50 relative z-10">
        <div className="container mx-auto px-4">
          <TextReveal>
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Loved by Real Estate Professionals
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Join hundreds of agents who have transformed their business
              </p>
            </div>
          </TextReveal>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2, duration: 0.6 }}
              >
                <Card className="p-8 h-full bg-white border border-gray-200 shadow-sm hover:shadow-lg transition-shadow">
                  <div className="flex gap-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-gray-700 mb-6 italic">"{testimonial.content}"</p>
                  <div>
                    <div className="font-bold text-gray-900">{testimonial.name}</div>
                    <div className="text-sm text-gray-600">{testimonial.role}</div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-white relative z-10">
        <div className="container mx-auto px-4">
          <TextReveal>
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Simple, Transparent Pricing
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Choose the plan that fits your business. All plans include 14-day free trial.
              </p>
            </div>
          </TextReveal>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {pricingTiers.map((tier, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                className={`relative ${tier.popular ? 'md:-mt-4 md:mb-4' : ''}`}
              >
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-blue-600 text-white text-sm font-semibold rounded-full shadow-sm">
                    Most Popular
                  </div>
                )}
                <Card className={`p-8 h-full bg-white border-2 shadow-lg hover:shadow-xl transition-shadow ${tier.popular ? 'border-blue-600' : 'border-gray-200'}`}>
                  <div className="text-center mb-6">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{tier.name}</h3>
                    <p className="text-gray-600 mb-4">{tier.description}</p>
                    <div className="flex items-baseline justify-center gap-2">
                      <span className="text-5xl font-bold text-gray-900">{tier.price}</span>
                      <span className="text-gray-600">{tier.period}</span>
                    </div>
                  </div>
                  <ul className="space-y-3 mb-8">
                    {tier.features.map((feature, i) => (
                      <li key={i} className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-blue-600 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  {!isAuthenticated && (
                    <Link href="/signup">
                      <Button className="w-full" size="lg" variant={tier.popular ? 'default' : 'outline'}>
                        Start Free Trial
                      </Button>
                    </Link>
                  )}
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-gray-900 relative z-10">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Transform Your Business?
            </h2>
            <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
              Join thousands of real estate professionals who have revolutionized their workflow with AI.
            </p>
            {!isAuthenticated && (
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/signup">
                  <Button size="lg" variant="secondary" className="text-lg px-8 py-6 shadow-lg">
                    Start Free Trial
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                </Link>
                <Link href="/signin">
                  <Button size="lg" variant="outline" className="text-white border-white hover:bg-white hover:text-gray-900 text-lg px-8 py-6">
                    Sign In
                  </Button>
                </Link>
              </div>
            )}
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 relative z-10">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Mail className="w-5 h-5 text-white" />
                </div>
                <span className="text-white font-semibold">RealInbox AI Pro</span>
              </div>
              <p className="text-sm">
                The all-in-one AI platform for real estate professionals. Transform your business with intelligent automation.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/integrations" className="hover:text-white transition-colors">Integrations</Link></li>
                <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
                <li><Link href="/careers" className="hover:text-white transition-colors">Careers</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-white transition-colors">Terms</Link></li>
                <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
                <li><Link href="/gdpr" className="hover:text-white transition-colors">GDPR</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>&copy; {new Date().getFullYear()} RealInbox AI Pro. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
