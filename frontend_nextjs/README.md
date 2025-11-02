# RealInbox AI Pro Frontend

A cutting-edge Next.js 14+ frontend for RealInbox AI Pro, featuring WebGL backgrounds, neon cyberpunk aesthetics, and AI-powered real estate tools.

## Features

- **VisionHome AI**: Computer vision property scanning and virtual renovations
- **Neighborhood Whisper**: NLP/ML-powered neighborhood fit scores and forecasts
- **Unified Inbox & Calendar**: AI-powered email management and calendar suggestions
- **Analytics Dashboard**: Track productivity, leads, and ROI
- **Subscription Management**: Stripe-integrated pricing tiers

## Tech Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom neon theme
- **3D/WebGL**: Three.js + React Three Fiber
- **Animations**: Framer Motion
- **State**: Zustand + TanStack Query
- **Forms**: React Hook Form + Zod
- **UI Components**: Custom neon-styled components

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-key-here
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your-key-here
```

3. Run development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend_nextjs/
├── app/              # Next.js App Router pages
├── components/       # Reusable UI components
├── lib/              # Utilities, hooks, stores
├── features/         # Feature-specific components
└── public/          # Static assets
```

## Key Features

- **WebGL Background**: Interactive particle system with mouse-reactive distortion
- **Neon Aesthetics**: Cyberpunk-inspired design with neon gradients and glows
- **Responsive Design**: Mobile-first approach with Tailwind breakpoints
- **Real-time Updates**: WebSocket integration for live notifications
- **Performance Optimized**: Lazy loading, code splitting, image optimization

## Environment Variables

See `.env.local.example` for required environment variables.

## Build

```bash
npm run build
npm start
```

## License

Private - RealInbox AI Pro

