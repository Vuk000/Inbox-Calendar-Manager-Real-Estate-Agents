'use client';

import { useRef, useCallback, useState } from 'react';
import Webcam from 'react-webcam';
import { motion } from 'framer-motion';
import { Camera, Scan } from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';

interface CameraScanProps {
  onCapture: (imageSrc: string) => void;
  onScan?: () => void;
}

export function CameraScan({ onCapture, onScan }: CameraScanProps) {
  const webcamRef = useRef<Webcam>(null);
  const [isScanning, setIsScanning] = useState(false);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      onCapture(imageSrc);
    }
  }, [onCapture]);

  const handleScan = () => {
    setIsScanning(true);
    setTimeout(() => {
      setIsScanning(false);
      onScan?.();
    }, 2000);
  };

  return (
    <Card className="relative overflow-hidden">
      <div className="relative w-full h-96 bg-dark-purple rounded-lg overflow-hidden">
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          className="w-full h-full object-cover"
        />
        
        {/* HUD Overlay */}
        <div className="absolute inset-0 pointer-events-none">
          {/* Scanning lines */}
          {isScanning && (
            <motion.div
              className="absolute w-full h-1 bg-neon-cyan shadow-glow"
              animate={{ y: [0, 384, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          )}
          
          {/* Corner brackets */}
          <div className="absolute top-4 left-4 w-12 h-12 border-t-2 border-l-2 border-neon-cyan shadow-neon" />
          <div className="absolute top-4 right-4 w-12 h-12 border-t-2 border-r-2 border-neon-cyan shadow-neon" />
          <div className="absolute bottom-4 left-4 w-12 h-12 border-b-2 border-l-2 border-neon-cyan shadow-neon" />
          <div className="absolute bottom-4 right-4 w-12 h-12 border-b-2 border-r-2 border-neon-cyan shadow-neon" />
          
          {/* Center crosshair */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
            <div className="w-16 h-16 border-2 border-neon-pink/50 rounded-full" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-neon-pink rounded-full" />
          </div>
          
          {/* Progress indicator */}
          {isScanning && (
            <div className="absolute bottom-20 left-1/2 -translate-x-1/2">
              <div className="flex items-center gap-2 text-neon-cyan font-orbitron">
                <Scan className="w-5 h-5 animate-spin" />
                <span>Scanning...</span>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Controls */}
      <div className="mt-4 flex gap-4 justify-center">
        <Button onClick={capture} variant="primary" glow>
          <Camera className="w-5 h-5 mr-2" />
          Capture
        </Button>
        {onScan && (
          <Button onClick={handleScan} variant="secondary" disabled={isScanning}>
            <Scan className="w-5 h-5 mr-2" />
            AI Scan
          </Button>
        )}
      </div>
    </Card>
  );
}

