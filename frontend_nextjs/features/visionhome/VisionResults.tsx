'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { PropertyCard } from '@/components/PropertyCard';
import { Card } from '@/components/ui/card';
import { useAPI } from '@/lib/hooks/useAPI';
import { visionAPI } from '@/lib/api';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { Loader2 } from 'lucide-react';

interface VisionResultsProps {
  limit?: number;
}

export function VisionResults({ limit = 20 }: VisionResultsProps) {
  const [page, setPage] = useState(1);

  // Fetch results from API
  const { data: resultsData, isLoading } = useAPI(
    ['vision-scans', page],
    () => visionAPI.listVisionScans({ page, limit }),
    { enabled: true }
  );

  const results = resultsData?.items || resultsData || [];
  const hasMore = results.length === limit;

  const loadMore = () => {
    if (!isLoading && hasMore) {
      setPage((prev) => prev + 1);
    }
  };

  return (
    <div className="space-y-6">
      {/* Masonry Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {results.map((result: any, index: number) => (
          <motion.div
            key={result.id}
            variants={fadeInUp}
            initial="hidden"
            animate="visible"
            transition={{ delay: index * 0.05 }}
            whileHover={{ y: -5 }}
          >
            <PropertyCard
              id={result.id}
              title={result.property_address || `Property ${result.id}`}
              address={result.property_address}
              fitScore={result.confidence_score}
              onClick={() => (window.location.href = `/visionhome/preview/${result.id}`)}
            />
          </motion.div>
        ))}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center py-8">
          <Loader2 className="w-8 h-8 text-neon-cyan animate-spin" />
        </div>
      )}

      {/* Load More Button */}
      {hasMore && !isLoading && (
        <div className="flex justify-center">
          <motion.button
            onClick={loadMore}
            className="px-6 py-3 border border-neon-cyan rounded-lg hover:bg-neon-cyan/10 transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Load More
          </motion.button>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && results.length === 0 && (
        <Card className="p-12 text-center">
          <p className="text-gray-400">No vision scans found</p>
        </Card>
      )}
    </div>
  );
}
