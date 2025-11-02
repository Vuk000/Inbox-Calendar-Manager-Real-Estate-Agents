'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { CameraScan } from '@/components/CameraScan';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { UpsellModal } from '@/components/UpsellModal';
import { useAPIMutation } from '@/lib/hooks/useAPI';
import { visionAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { Upload, Camera } from 'lucide-react';
import toast from 'react-hot-toast';
import { fadeInUp } from '@/lib/hooks/useAnimation';

export default function VisionHomePage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [showUpsell, setShowUpsell] = useState(false);
  const [uploading, setUploading] = useState(false);

  const analyzeMutation = useAPIMutation(
    async (data: { file: File; address?: string }) => {
      return visionAPI.analyzePropertyImage(data.file, data.address);
    },
    {
      onSuccess: (data) => {
        toast.success('Property analyzed successfully!');
        router.push(`/visionhome/preview/${data.id}`);
      },
      onError: (error: any) => {
        if (error.response?.status === 403) {
          setShowUpsell(true);
        } else {
          toast.error(error.response?.data?.detail || 'Failed to analyze property');
        }
      },
    }
  );

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await analyzeMutation.mutateAsync({ file });
    } finally {
      setUploading(false);
    }
  };

  const handleCapture = async (imageSrc: string) => {
    // Convert data URL to File
    const response = await fetch(imageSrc);
    const blob = await response.blob();
    const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });

    setUploading(true);
    try {
      await analyzeMutation.mutateAsync({ file });
    } finally {
      setUploading(false);
    }
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
              VisionHome AI
            </h1>
            <p className="text-gray-400">Scan properties with computer vision and get instant insights</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Camera Interface */}
            <Card className="p-6">
              <h2 className="text-2xl font-orbitron text-neon-cyan mb-4 flex items-center gap-2">
                <Camera className="w-6 h-6" />
                Camera Scan
              </h2>
              <CameraScan onCapture={handleCapture} />
            </Card>

            {/* Upload Interface */}
            <Card className="p-6">
              <h2 className="text-2xl font-orbitron text-neon-pink mb-4 flex items-center gap-2">
                <Upload className="w-6 h-6" />
                Upload Image
              </h2>
              <div className="border-2 border-dashed border-neon-cyan/30 rounded-lg p-8 text-center hover:border-neon-cyan transition-colors">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                  disabled={uploading}
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center gap-4"
                >
                  <Upload className="w-12 h-12 text-neon-cyan" />
                  <div>
                    <p className="text-lg font-medium text-neon-cyan mb-1">
                      {uploading ? 'Analyzing...' : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-sm text-gray-400">
                      PNG, JPG, GIF up to 10MB
                    </p>
                  </div>
                  <Button variant="secondary" disabled={uploading}>
                    {uploading ? 'Processing...' : 'Select File'}
                  </Button>
                </label>
              </div>
            </Card>
          </div>

          <UpsellModal
            isOpen={showUpsell}
            onClose={() => setShowUpsell(false)}
            title="Upgrade Required"
            message="You've reached your monthly limit for VisionHome scans. Upgrade to Pro for unlimited scans!"
            feature="VisionHome AI"
            ctaText="Upgrade Now"
            onCtaClick={() => router.push('/subscription')}
          />
        </motion.div>
      </div>
    </div>
  );
}

