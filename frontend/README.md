# RealInbox AI - Frontend

Modern React + TypeScript frontend for the RealInbox AI platform.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Zustand** for state management
- **TanStack Query** (React Query) for server state
- **Axios** for API calls
- **React Hot Toast** for notifications
- **Heroicons** for icons
- **Framer Motion** for animations

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   └── Layout.tsx    # Main app layout with sidebar
│   ├── pages/            # Page components
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── InboxPage.tsx
│   │   ├── DraftsPage.tsx
│   │   ├── TasksPage.tsx
│   │   ├── PropertiesPage.tsx
│   │   ├── AnalyticsPage.tsx
│   │   └── SettingsPage.tsx
│   ├── services/         # API service layer
│   │   └── api.ts        # Axios instance and API functions
│   ├── stores/           # Zustand stores
│   │   └── authStore.ts  # Authentication state
│   ├── App.tsx           # Main app component with routing
│   ├── main.tsx          # App entry point
│   └── index.css         # Global styles with Tailwind
├── public/               # Static assets
├── index.html            # HTML template
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── vite.config.ts        # Vite config
├── tailwind.config.js    # Tailwind config
└── README.md             # This file
```

## Features Implemented

### ✅ Current Features
- User authentication (login/register)
- Protected routes
- Responsive layout with sidebar navigation
- Dashboard with placeholder metrics
- Modern UI with Tailwind CSS
- API integration layer ready
- State management with Zustand
- Toast notifications

### 🚧 In Progress
- Email inbox with AI triage
- Draft generation interface
- Task management board
- Property dashboard
- Analytics and reports
- Settings and integrations

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## API Integration

The app uses Axios with interceptors for:
- Automatic token attachment
- Token refresh on 401 errors
- Error handling with toast notifications

See `src/services/api.ts` for all API service functions.

## Styling

- Using Tailwind CSS with custom theme colors
- Custom utility classes in `index.css`
- Responsive design (mobile-first)
- Dark mode support (planned)

## Development Tips

1. **Hot Module Replacement**: Vite provides instant HMR
2. **TypeScript**: Strict mode enabled for type safety
3. **Code Splitting**: Automatic route-based code splitting
4. **API Proxy**: Vite proxy configured for `/api` requests

## Deployment

### Build

```bash
npm run build
```

Output will be in `dist/` directory.

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Deploy to Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Android)

## Performance

- Lighthouse Score Target: 90+
- First Contentful Paint: <1.5s
- Time to Interactive: <3.5s
- Code splitting for optimal bundle sizes

## License

Proprietary - All rights reserved

