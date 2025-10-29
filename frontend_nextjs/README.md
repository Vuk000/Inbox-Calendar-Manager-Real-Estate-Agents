# AgentFlow Frontend (Next.js)

Modern Next.js frontend for AgentFlow - AI-powered Real Estate CRM.

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend_nextjs
npm install
# or
pnpm install
```

### 2. Environment Configuration

Create a `.env.local` file in the `frontend_nextjs` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_APP_NAME=AgentFlow
NEXT_PUBLIC_APP_ENV=development
```

### 3. Run Development Server

```bash
npm run dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend_nextjs/
├── app/                    # Next.js App Router
│   ├── dashboard/          # Protected dashboard pages
│   │   ├── page.tsx        # Dashboard home
│   │   ├── contacts/       # Contacts management
│   │   ├── inbox/          # Email inbox
│   │   ├── drafts/         # AI-generated drafts
│   │   ├── tasks/          # Task management
│   │   ├── calendar/       # Calendar & meetings
│   │   ├── analytics/      # Analytics & reports
│   │   ├── properties/     # Property listings
│   │   ├── settings/       # User settings
│   │   └── layout.tsx      # Dashboard layout
│   ├── login/              # Login page
│   ├── signup/             # Signup page
│   ├── layout.tsx          # Root layout
│   └── globals.css         # Global styles
├── components/             # Reusable components
│   └── ui/                 # shadcn/ui components
├── lib/                    # Utilities and libraries
│   ├── api.ts              # API client & services
│   ├── stores/             # Zustand stores
│   │   └── authStore.ts    # Authentication state
│   └── utils.ts            # Utility functions
├── middleware.ts           # Next.js middleware
└── public/                 # Static assets
```

## Features

### Authentication
- JWT-based authentication
- Automatic token refresh
- Protected routes
- Zustand for state management

### Pages
- **Dashboard**: Overview with stats and recent activity
- **Contacts**: Contact management with timeline
- **Inbox**: AI-triaged email inbox
- **Drafts**: AI-generated email responses
- **Tasks**: Kanban-style task board
- **Calendar**: Meeting scheduler
- **Analytics**: Business metrics and reports
- **Properties**: Property listings
- **Settings**: User preferences and integrations

### API Integration
- Axios-based HTTP client
- Automatic authentication headers
- Error handling with toast notifications
- TypeScript type safety

### Real-time Updates
- WebSocket support (ready for implementation)
- Live email notifications
- Task updates
- Activity stream

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui + Radix UI
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Charts**: Recharts
- **Notifications**: React Hot Toast

## Development

### Code Style
- TypeScript strict mode
- ESLint configuration
- Prettier for formatting

### Testing
```bash
npm run test        # Run tests
npm run test:ui     # Run tests with UI
```

## Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main

### Environment Variables for Production
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://your-api-domain.com/ws
NEXT_PUBLIC_APP_ENV=production
```

## Backend Integration

This frontend connects to the FastAPI backend at `/api/v1`. Make sure the backend is running at the URL specified in `NEXT_PUBLIC_API_URL`.

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Notes

- The frontend uses localStorage for authentication state persistence
- Protected routes automatically redirect to `/login` if not authenticated
- API errors are displayed as toast notifications
- The UI follows a glassmorphism design with vibrant colors
