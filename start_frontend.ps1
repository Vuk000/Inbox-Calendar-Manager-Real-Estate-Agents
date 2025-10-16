# RealInbox AI - Frontend Development Server Startup Script

Write-Host "🎨 Starting RealInbox AI Frontend" -ForegroundColor Green

# Navigate to frontend directory
Set-Location frontend

# Start the development server
Write-Host "📡 Starting on http://localhost:5173`n" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

npm run dev

