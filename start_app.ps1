# PowerShell script to start backend server
# Run with: .\start_app.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting AgentFlow - Backend" -ForegroundColor Cyan
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

Write-Host "Starting backend server..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend will run on: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start backend
Push-Location backend
if (Test-Path "venv\Scripts\activate.bat") {
    & "venv\Scripts\activate.bat"
    python -m uvicorn app.main:app --reload
} else {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\activate.bat"
    pip install -r requirements.txt
    python -m uvicorn app.main:app --reload
}
Pop-Location

