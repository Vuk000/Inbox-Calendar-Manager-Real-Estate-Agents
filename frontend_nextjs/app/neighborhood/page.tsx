'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { FitScoreChart } from '@/components/FitScoreChart';
import { UpsellModal } from '@/components/UpsellModal';
import { useAPIMutation } from '@/lib/hooks/useAPI';
import { neighborhoodAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import NeonMap from '@/components/NeonMap';
import { Search, MapPin } from 'lucide-react';
import toast from 'react-hot-toast';
import { fadeInUp } from '@/lib/hooks/useAnimation';

export default function NeighborhoodPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [query, setQuery] = useState('');
  const [showUpsell, setShowUpsell] = useState(false);

  const searchMutation = useAPIMutation(
    async (data: { query: string }) => {
      return neighborhoodAPI.searchNeighborhood(data.query);
    },
    {
      onSuccess: (data) => {
        toast.success('Neighborhood analysis complete!');
        router.push(`/neighborhood/report/${data.id}`);
      },
      onError: (error: any) => {
        if (error.response?.status === 403) {
          setShowUpsell(true);
        } else {
          toast.error(error.response?.data?.detail || 'Failed to analyze neighborhood');
        }
      },
    }
  );

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    searchMutation.mutate({ query });
  };

  if (!isAuthenticated) {
    router.push('/');
    return null;
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 md:ml-64 p-4 md:p-8">
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          className="space-y-8"
        >
          <div>
            <h1 className="text-4xl font-orbitron font-bold text-transparent bg-clip-text bg-gradient-neon mb-2">
              Neighborhood Whisper
            </h1>
            <p className="text-gray-400">AI-powered neighborhood fit scores and insights</p>
          </div>

          <Card className="p-6">
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    label="Search Neighborhood"
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., family-friendly neighborhood in Seattle"
                    required
                  />
                </div>
                <div className="flex items-end">
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={searchMutation.isPending}
                    glow
                  >
                    <Search className="w-5 h-5 mr-2" />
                    {searchMutation.isPending ? 'Analyzing...' : 'Search'}
                  </Button>
                </div>
              </div>
            </form>
          </Card>

          {/* Map Placeholder */}
          <Card className="p-6">
            <h2 className="text-2xl font-orbitron text-neon-cyan mb-4 flex items-center gap-2">
              <MapPin className="w-6 h-6" />
              Interactive Map
            </h2>
            <div className="w-full h-96 rounded-lg overflow-hidden border border-neon-cyan/20">
              <NeonMap
                center={{ lat: 47.6062, lng: -122.3321 }} // Default to Seattle
                zoom={12}
                markers={[
                  { lat: 47.6062, lng: -122.3321, label: 'Sample Location', fitScore: 85 },
                ]}
              />
            </div>
          </Card>

          {/* Sample Fit Scores */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <FitScoreChart score={85} label="Amenities" />
            <FitScoreChart score={78} label="Safety" />
            <FitScoreChart score={92} label="Eco Score" />
          </div>

          <UpsellModal
            isOpen={showUpsell}
            onClose={() => setShowUpsell(false)}
            title="Upgrade Required"
            message="You've reached your monthly limit for neighborhood searches. Upgrade to Pro for unlimited searches!"
            feature="Neighborhood Whisper"
            ctaText="Upgrade Now"
            onCtaClick={() => router.push('/subscription')}
          />
        </motion.div>
      </div>
    </div>
  );
}

