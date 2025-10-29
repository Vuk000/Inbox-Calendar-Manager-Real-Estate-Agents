# Deployment Guide

## Vercel Deployment

### Prerequisites
1. Vercel account
2. GitHub repository connected
3. Backend API URL configured

### Frontend Deployment Steps

1. **Install Vercel CLI** (optional)
   ```bash
   npm i -g vercel
   ```

2. **Deploy from Vercel Dashboard**
   - Go to https://vercel.com
   - Import your GitHub repository
   - Select the `frontend_nextjs` directory as the root
   - Configure environment variables (see below)

3. **Environment Variables**
   Set these in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api.com/api/v1
   NEXT_PUBLIC_WS_URL=wss://your-backend-api.com/ws
   NEXT_PUBLIC_APP_NAME=AgentFlow
   NEXT_PUBLIC_APP_ENV=production
   ```

4. **Build Settings**
   - Framework Preset: Next.js
   - Build Command: `npm run build` (or `npm run build --legacy-peer-deps` if needed)
   - Output Directory: `.next`
   - Install Command: `npm install --legacy-peer-deps`

### Backend CORS Configuration

Update `backend/app/config.py` to include your Vercel deployment URL:

```python
CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://your-app.vercel.app,https://*.vercel.app"
```

For production, set this in your backend's environment variables.

### Production Environment Variables

**Frontend (.env.local for local, Vercel env vars for production):**
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws
```

**Backend (.env):**
```
CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app
```

### Troubleshooting

1. **CORS Errors**
   - Ensure backend CORS_ORIGINS includes your Vercel URL
   - Check that CORS_CREDENTIALS is True

2. **WebSocket Connection Issues**
   - Verify NEXT_PUBLIC_WS_URL uses `wss://` for production
   - Check backend WebSocket endpoint is accessible

3. **Build Errors**
   - Use `--legacy-peer-deps` flag if React version conflicts occur
   - Check Node.js version (should be 18+)

4. **API Connection**
   - Verify NEXT_PUBLIC_API_URL is correctly set
   - Check backend is accessible from Vercel's servers
   - Review Vercel function logs for API errors

### Post-Deployment Checklist

- [ ] Test login/signup flow
- [ ] Verify API connectivity
- [ ] Test WebSocket connection
- [ ] Check all pages load correctly
- [ ] Verify environment variables are set
- [ ] Test CRUD operations
- [ ] Check error handling
- [ ] Verify mobile responsiveness

