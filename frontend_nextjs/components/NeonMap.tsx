'use client';

import { useRef, useEffect, useState } from 'react';
import { Wrapper, Status } from '@googlemaps/react-wrapper';
import { ReactElement } from 'react';

interface MapProps {
  center: { lat: number; lng: number };
  zoom: number;
  markers?: Array<{ lat: number; lng: number; label?: string; fitScore?: number }>;
  className?: string;
}

function MapComponent({ center, zoom, markers = [] }: MapProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);

  useEffect(() => {
    if (ref.current && !map && typeof window !== 'undefined' && window.google) {
      const newMap = new google.maps.Map(ref.current, {
        center,
        zoom,
        styles: [
          {
            featureType: 'all',
            elementType: 'geometry',
            stylers: [{ color: '#1A0033' }],
          },
          {
            featureType: 'all',
            elementType: 'labels.text.fill',
            stylers: [{ color: '#00FFFF' }],
          },
          {
            featureType: 'water',
            elementType: 'geometry',
            stylers: [{ color: '#0A0E27' }],
          },
          {
            featureType: 'road',
            elementType: 'geometry',
            stylers: [{ color: '#0A0E27' }],
          },
        ],
      });
      setMap(newMap);
    }
  }, [ref, map, center, zoom]);

  useEffect(() => {
    if (map && markers.length > 0 && typeof window !== 'undefined' && window.google) {
      markers.forEach((marker) => {
        const googleMarker = new google.maps.Marker({
          position: { lat: marker.lat, lng: marker.lng },
          map,
          label: marker.label,
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: marker.fitScore && marker.fitScore > 80 ? '#00FFFF' : '#FF00FF',
            fillOpacity: 1,
            strokeColor: '#FFFFFF',
            strokeWeight: 2,
          },
        });

        if (marker.fitScore) {
          const infoWindow = new google.maps.InfoWindow({
            content: `<div style="color: #00FFFF; font-family: 'Orbitron', sans-serif;">
              <strong>Fit Score: ${marker.fitScore}%</strong>
              ${marker.label ? `<br>${marker.label}` : ''}
            </div>`,
          });

          googleMarker.addListener('click', () => {
            infoWindow.open(map, googleMarker);
          });
        }
      });
    }
  }, [map, markers]);

  return <div ref={ref} className="w-full h-full rounded-lg" />;
}

const render = (status: Status): ReactElement => {
  if (status === Status.LOADING) {
    return <div className="w-full h-full flex items-center justify-center bg-dark-purple rounded-lg">Loading map...</div>;
  }
  if (status === Status.FAILURE) {
    return <div className="w-full h-full flex items-center justify-center bg-dark-purple rounded-lg text-red-500">Error loading map</div>;
  }
  return <div className="w-full h-full bg-dark-purple rounded-lg" />;
};

export default function NeonMap({ center, zoom, markers, className = '' }: MapProps) {
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

  if (!apiKey) {
    return (
      <div className={`w-full h-full flex items-center justify-center bg-dark-purple rounded-lg border border-neon-cyan/20 ${className}`}>
        <p className="text-gray-400">Google Maps API key not configured</p>
      </div>
    );
  }

  return (
    <div className={`w-full h-full ${className}`}>
      <Wrapper apiKey={apiKey} render={render}>
        <MapComponent center={center} zoom={zoom} markers={markers} />
      </Wrapper>
    </div>
  );
}

