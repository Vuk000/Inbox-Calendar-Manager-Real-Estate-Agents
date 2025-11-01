# PowerShell script to start both servers
# Run with: .\start_app.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting AgentFlow - Backend + Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the project root
if (-not (Test-Path "backend\app\main.py")) {
    Write-Host "Error: This script must be run from the project root directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Check if backend virtual environment exists
if (-not (Test-Path "backend\venv\Scripts\activate.bat")) {
    Write-Host "Backend virtual environment not found!" -ForegroundColor Yellow
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    Push-Location backend
    python -m venv venv
    Write-Host ""
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    & "venv\Scripts\activate.bat"
    pip install -r requirements.txt
    Pop-Location
    Write-Host ""
}

# Check if frontend node_modules exists
if (-not (Test-Path "frontend_nextjs\node_modules")) {
    Write-Host "Frontend dependencies not found!" -ForegroundColor Yellow
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location frontend_nextjs
    npm install
    Pop-Location
    Write-Host ""
}

Write-Host "Starting both servers..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend will run on: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend will run on: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop both servers" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start backend in a new window
$backendScript = @"
cd /d `"$PWD\backend`"
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python -m uvicorn app.main:app --reload
) else (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    python -m uvicorn app.main:app --reload
)
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in current window
Push-Location frontend_nextjs
Write-Host ""
Write-Host "Frontend starting on http://localhost:3000" -ForegroundColor Green
Write-Host "Backend is running in a separate window" -ForegroundColor Green
Write-Host ""
npm run dev

