'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { HolographicCard } from '@/components/cyberpunk/HolographicCard';
import { ScrollReveal } from '@/components/cyberpunk/ScrollReveal';
import { NeonText } from '@/components/cyberpunk/NeonText';
import { NeonButton } from '@/components/cyberpunk/NeonButton';
import { Button } from '@/components/ui/button';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { subscriptionAPI, paymentsAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { Check, Sparkles, Loader2 } from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { loadStripe } from '@stripe/stripe-js';
import toast from 'react-hot-toast';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '');

const tiers = [
  {
    name: 'Free',
    value: 'free_trial',
    price: '$0',
    features: ['5 Vision scans/month', '10 Neighborhood searches/month', 'Basic inbox management'],
    color: 'border-gray-600',
  },
  {
    name: 'Solo',
    value: 'solo_agent',
    price: '$29',
    features: ['50 Vision scans/month', '100 Neighborhood searches/month', 'Advanced AI features'],
    color: 'border-neon-cyan',
  },
  {
    name: 'Pro',
    value: 'pro_agent',
    price: '$99',
    features: ['Unlimited Vision scans', 'Unlimited searches', 'Everything in Solo', 'Priority support'],
    color: 'border-neon-pink',
  },
];

export default function SubscriptionPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const { data: usage, isLoading: usageLoading } = useAPI(
    ['subscription', 'usage'],
    () => subscriptionAPI.getUsage(),
    { enabled: isAuthenticated }
  );

  const checkoutMutation = useAPIMutation(
    async ({ tier }: { tier: string }) => {
      const successUrl = `${window.location.origin}/subscription?success=true`;
      const cancelUrl = `${window.location.origin}/subscription?canceled=true`;
      return paymentsAPI.createCheckoutSession(tier, successUrl, cancelUrl);
    },
    {
      onSuccess: async (data) => {
        const stripe = await stripePromise;
        if (stripe && data.checkout_url) {
          // Redirect to Stripe Checkout
          window.location.href = data.checkout_url;
        } else {
          toast.error('Failed to initialize Stripe checkout');
        }
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create checkout session');
      },
    }
  );

  if (!isAuthenticated) {
    router.push('/');
    return null;
  }

  const handleCheckout = async (tier: string) => {
    if (tier === 'free_trial') {
      toast('You are already on the free tier', { icon: 'ℹ️' });
      return;
    }
    checkoutMutation.mutate({ tier });
  };

  return (
    <div className="flex min-h-screen bg-dark-bg">
      <Sidebar />
      <div className="flex-1 md:ml-64 p-4 md:p-8">
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          className="space-y-8"
        >
          <ScrollReveal>
            <div>
              <h1 className="text-4xl font-orbitron font-bold mb-2">
                <NeonText color="purple">Subscription Plans</NeonText>
              </h1>
              <p className="text-gray-400">Choose the plan that fits your needs</p>
            </div>
          </ScrollReveal>

          {/* Usage Summary */}
          {usage && (
            <Card className="p-6">
              <h2 className="text-2xl font-orbitron text-neon-cyan mb-4">Current Usage</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-400 mb-1">Vision Scans</p>
                  <p className="text-xl font-bold text-neon-cyan">
                    {usage.usage?.vision_scans || 0} / {usage.limits?.vision_scans || 0}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Neighborhood Searches</p>
                  <p className="text-xl font-bold text-neon-pink">
                    {usage.usage?.neighborhood_searches || 0} / {usage.limits?.neighborhood_searches || 0}
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Pricing Tiers */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {tiers.map((tier, index) => {
              const isCurrentTier = usage?.subscription_tier === tier.value;
              return (
                <motion.div
                  key={tier.name}
                  variants={fadeInUp}
                  initial="hidden"
                  animate="visible"
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.05, y: -5 }}
                >
                  <Card className={`p-6 h-full flex flex-col border-2 ${tier.color} ${isCurrentTier ? 'bg-neon-cyan/10' : ''}`}>
                    <div className="flex items-center gap-2 mb-4">
                      <Sparkles className="w-6 h-6 text-neon-cyan" />
                      <h3 className="text-2xl font-orbitron font-bold">{tier.name}</h3>
                      {isCurrentTier && (
                        <span className="ml-auto px-2 py-1 text-xs bg-neon-cyan/20 text-neon-cyan rounded">
                          Current
                        </span>
                      )}
                    </div>
                    <p className="text-4xl font-bold text-neon-cyan mb-6">{tier.price}/month</p>
                    <ul className="flex-1 space-y-3 mb-6">
                      {tier.features.map((feature) => (
                        <li key={feature} className="flex items-center gap-2 text-gray-300">
                          <Check className="w-5 h-5 text-neon-cyan flex-shrink-0" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button
                      variant={tier.name === 'Pro' ? 'primary' : 'secondary'}
                      className="w-full"
                      onClick={() => handleCheckout(tier.value)}
                      disabled={isCurrentTier || checkoutMutation.isPending}
                      glow={tier.name === 'Pro' && !isCurrentTier}
                    >
                      {checkoutMutation.isPending ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : isCurrentTier ? (
                        'Current Plan'
                      ) : (
                        'Upgrade'
                      )}
                    </Button>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      </div>
    </div>
  );
}

