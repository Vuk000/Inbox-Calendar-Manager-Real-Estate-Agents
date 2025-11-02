'use client';

import { use } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sidebar } from '@/components/Sidebar';
import { useAPI } from '@/lib/hooks/useAPI';
import { neighborhoodAPI } from '@/lib/api';
import { ArrowLeft, Download } from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';

export default function NeighborhoodReportPage() {
  const router = useRouter();
  const params = useParams();
  const id = Number(params.id);
  const { isAuthenticated } = useAuth();

  const { data: report, isLoading } = useAPI(
    ['neighborhood', id],
    () => neighborhoodAPI.getNeighborhoodReport(id),
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
              Neighborhood Report
            </h1>

            {report && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="p-4">
                    <h3 className="text-lg font-orbitron text-neon-cyan mb-2">Fit Score</h3>
                    <p className="text-3xl font-bold text-neon-pink">{report.fit_score || 'N/A'}%</p>
                  </Card>
                  <Card className="p-4">
                    <h3 className="text-lg font-orbitron text-neon-pink mb-2">Location</h3>
                    <p className="text-gray-300">{report.location || 'N/A'}</p>
                  </Card>
                  <Card className="p-4">
                    <h3 className="text-lg font-orbitron text-neon-purple mb-2">Eco Score</h3>
                    <p className="text-2xl font-bold text-neon-cyan">{report.eco_score || 'N/A'}%</p>
                  </Card>
                </div>

                {/* Charts Placeholder */}
                <div className="w-full h-64 bg-dark-purple rounded-lg flex items-center justify-center border border-neon-cyan/20">
                  <p className="text-gray-400">Forecast charts placeholder</p>
                </div>

                {/* Export Button */}
                <div className="flex justify-end">
                  <Button variant="secondary">
                    <Download className="w-4 h-4 mr-2" />
                    Export PDF
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </motion.div>
      </div>
    </div>
  );
}

