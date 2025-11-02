'use client';

import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { motion } from 'framer-motion';
import { Card } from './card';

interface ChartProps {
  data: Array<Record<string, any>>;
  title?: string;
  className?: string;
}

const COLORS = ['#00FFFF', '#FF00FF', '#00FFAA', '#FFAA00', '#AA00FF'];

// Line Chart Component
export function LineChartComponent({ data, title, className }: ChartProps) {
  const keys = data.length > 0 ? Object.keys(data[0]).filter((k) => k !== 'name') : [];

  return (
    <Card className={className}>
      {title && (
        <h3 className="text-xl font-orbitron text-neon-cyan mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 255, 255, 0.1)" />
          <XAxis dataKey="name" stroke="#00FFFF" />
          <YAxis stroke="#00FFFF" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1A0033',
              border: '1px solid #00FFFF',
              borderRadius: '8px',
              color: '#00FFFF',
            }}
          />
          <Legend />
          {keys.map((key, index) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={COLORS[index % COLORS.length]}
              strokeWidth={2}
              dot={{ fill: COLORS[index % COLORS.length], r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

// Bar Chart Component
export function BarChartComponent({ data, title, className }: ChartProps) {
  const keys = data.length > 0 ? Object.keys(data[0]).filter((k) => k !== 'name') : [];

  return (
    <Card className={className}>
      {title && (
        <h3 className="text-xl font-orbitron text-neon-cyan mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 255, 255, 0.1)" />
          <XAxis dataKey="name" stroke="#00FFFF" />
          <YAxis stroke="#00FFFF" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1A0033',
              border: '1px solid #00FFFF',
              borderRadius: '8px',
              color: '#00FFFF',
            }}
          />
          <Legend />
          {keys.map((key, index) => (
            <Bar
              key={key}
              dataKey={key}
              fill={COLORS[index % COLORS.length]}
              radius={[8, 8, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

// Pie Chart Component
interface PieChartProps {
  data: Array<{ name: string; value: number }>;
  title?: string;
  className?: string;
}

export function PieChartComponent({ data, title, className }: PieChartProps) {
  return (
    <Card className={className}>
      {title && (
        <h3 className="text-xl font-orbitron text-neon-cyan mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1A0033',
              border: '1px solid #00FFFF',
              borderRadius: '8px',
              color: '#00FFFF',
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
}

// Area Chart Component
export function AreaChartComponent({ data, title, className }: ChartProps) {
  const keys = data.length > 0 ? Object.keys(data[0]).filter((k) => k !== 'name') : [];

  return (
    <Card className={className}>
      {title && (
        <h3 className="text-xl font-orbitron text-neon-cyan mb-4">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            {keys.map((key, index) => (
              <linearGradient key={key} id={`color${index}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COLORS[index % COLORS.length]} stopOpacity={0.8} />
                <stop offset="95%" stopColor={COLORS[index % COLORS.length]} stopOpacity={0} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 255, 255, 0.1)" />
          <XAxis dataKey="name" stroke="#00FFFF" />
          <YAxis stroke="#00FFFF" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1A0033',
              border: '1px solid #00FFFF',
              borderRadius: '8px',
              color: '#00FFFF',
            }}
          />
          <Legend />
          {keys.map((key, index) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stroke={COLORS[index % COLORS.length]}
              fill={`url(#color${index})`}
              strokeWidth={2}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
}

// Sparkline Chart Component
interface SparklineProps {
  data: number[];
  color?: string;
  height?: number;
  className?: string;
}

export function SparklineChart({ data, color = '#00FFFF', height = 40, className }: SparklineProps) {
  const chartData = data.map((value, index) => ({ name: index, value }));

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData}>
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={false}
            isAnimationActive={true}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// Animated Number Counter
interface AnimatedCounterProps {
  value: number;
  duration?: number;
  className?: string;
  prefix?: string;
  suffix?: string;
  decimals?: number;
}

export function AnimatedCounter({
  value,
  duration = 1,
  className,
  prefix = '',
  suffix = '',
  decimals = 0,
}: AnimatedCounterProps) {
  const [displayValue, setDisplayValue] = React.useState(0);

  React.useEffect(() => {
    let startTime: number;
    const startValue = displayValue;
    const endValue = value;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / (duration * 1000), 1);
      const current = startValue + (endValue - startValue) * progress;
      setDisplayValue(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setDisplayValue(endValue);
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  return (
    <motion.span
      className={className}
      initial={{ scale: 0.8 }}
      animate={{ scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      {prefix}
      {displayValue.toFixed(decimals)}
      {suffix}
    </motion.span>
  );
}

