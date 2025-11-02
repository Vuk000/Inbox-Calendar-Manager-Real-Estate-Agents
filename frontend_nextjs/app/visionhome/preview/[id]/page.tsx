'use client';

import { use } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sidebar } from '@/components/Sidebar';
import { useAPI } from '@/lib/hooks/useAPI';
import { visionAPI } from '@/lib/api';
import { ArrowLeft, Share2, Download } from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';

export default function VisionHomePreviewPage() {
  const router = useRouter();
  const params = useParams();
  const id = Number(params.id);
  const { isAuthenticated } = useAuth();

  const { data: scan, isLoading } = useAPI(
    ['vision', id],
    () => visionAPI.getVisionScan(id),
    { enabled: !!id }
  );

  if (!isAuthenticated) {
    router.push('/');
    return null;
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 md:ml-64 p-4 md:p-8 flex items-center justify-center">
          <div className="spinner w-12 h-12" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 md:ml-64 p-4 md:p-8">
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          <Card className="p-6">
            <h1 className="text-3xl font-orbitron font-bold text-neon-cyan mb-6">
              Vision Scan Results
            </h1>

            {/* 3D Viewer Placeholder */}
            <div className="w-full h-96 bg-dark-purple rounded-lg mb-6 flex items-center justify-center border border-neon-cyan/20">
              <p className="text-gray-400">Interactive 3D Viewer Placeholder</p>
            </div>

            {/* Analysis Results */}
            {scan && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className="p-4">
                    <h3 className="text-lg font-orbitron text-neon-cyan mb-2">Property Details</h3>
                    <p className="text-gray-300">{scan.property_address || 'N/A'}</p>
                  </Card>
                  <Card className="p-4">
                    <h3 className="text-lg font-orbitron text-neon-pink mb-2">Confidence Score</h3>
                    <p className="text-2xl font-bold text-neon-pink">{scan.confidence_score || 'N/A'}%</p>
                  </Card>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="mt-6 flex gap-4">
              <Button variant="secondary">
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </Button>
              <Button variant="secondary">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}

