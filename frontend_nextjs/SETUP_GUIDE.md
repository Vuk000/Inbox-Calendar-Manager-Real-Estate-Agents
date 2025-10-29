# AgentFlow Frontend Setup Guide

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
cd frontend_nextjs
npm install
```

Or if you prefer pnpm:
```bash
pnpm install
```

### 2. Create Environment File

Create a file named `.env.local` in the `frontend_nextjs` directory with this content:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_APP_NAME=AgentFlow
NEXT_PUBLIC_APP_ENV=development
```

### 3. Start the Development Server

```bash
npm run dev
```

The app should now be running at `http://localhost:3000`

---

## Troubleshooting

### Issue: Styling looks broken or missing

**Solution:**
1. Make sure you ran `npm install` to install all dependencies
2. Delete `.next` folder and `node_modules`, then run `npm install` again
3. Restart the dev server

```bash
rm -rf .next node_modules
npm install
npm run dev
```

### Issue: API calls fail

**Solution:**
1. Make sure your backend is running at `http://localhost:8000`
2. Check that `.env.local` file exists and has the correct API_URL
3. Check browser console for CORS errors

### Issue: Dark mode is too dark / can't see anything

**Solution:**
The app is set to dark mode by default in `app/layout.tsx`. To change:

```typescript
// In app/layout.tsx, change this line:
<html lang="en" className="dark">

// To this for light mode:
<html lang="en">
```

### Issue: "Module not found" errors

**Solution:**
Make sure all dependencies are installed:

```bash
npm install axios zustand @tanstack/react-query react-hot-toast date-fns
```

---

## Testing the App

### 1. Test Landing Page
- Navigate to `http://localhost:3000`
- You should see the beautiful AgentFlow landing page
- Click "Sign In" or "Get Started"

### 2. Test Signup
- Go to `http://localhost:3000/signup`
- Fill in: First Name, Last Name, Email, Password
- Check "I agree to terms"
- Click "Create Account"
- **Backend must be running for this to work!**

### 3. Test Login
- Go to `http://localhost:3000/login`
- Enter credentials from signup
- Click "Sign In"
- You should be redirected to `/dashboard`

### 4. Test Dashboard
- After login, you should see the dashboard with:
  - Your name in the header
  - Real stats from backend
  - Recent activity
  - Priority contacts
- If data is empty, that's normal if backend has no data yet

---

## Backend Setup (Required for Full Functionality)

The frontend needs the backend running. In a separate terminal:

```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend should be at `http://localhost:8000`

---

## What's Working

✅ Landing page with animations
✅ Login / Signup pages
✅ Authentication (JWT tokens)
✅ Dashboard with real backend data
✅ Protected routes
✅ Toast notifications
✅ Dark mode styling
✅ Responsive design

## What Still Needs Backend Integration

⏳ Contacts page (uses mock data)
⏳ Inbox page (uses mock data)
⏳ Drafts page (uses mock data)
⏳ Tasks page (uses mock data)
⏳ Calendar page (uses mock data)
⏳ Analytics page (uses mock data)
⏳ Settings page (needs integration)
⏳ Properties page (uses mock data)

---

## Common Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

---

## File Structure

```
frontend_nextjs/
├── app/                    # Next.js App Router
│   ├── dashboard/          # Protected pages
│   ├── login/              # Login page ✅
│   ├── signup/             # Signup page ✅
│   ├── page.tsx            # Landing page ✅
│   ├── layout.tsx          # Root layout ✅
│   └── globals.css         # Global styles ✅
├── lib/
│   ├── api.ts              # API client ✅
│   └── stores/
│       └── authStore.ts    # Auth state ✅
├── components/
│   └── ui/                 # shadcn/ui components ✅
├── .env.local              # Environment variables (CREATE THIS!)
└── package.json
```

---

## Need Help?

1. Check browser console for errors
2. Check terminal for Next.js errors
3. Make sure backend is running
4. Verify `.env.local` exists and is correct
5. Try deleting `.next` and `node_modules` and reinstalling

