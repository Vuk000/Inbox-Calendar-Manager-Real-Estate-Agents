# PowerShell script to verify development environment setup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AgentFlow - Environment Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Get-Location
$errors = 0
$warnings = 0

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Python found: $pythonCheck" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Python not found" -ForegroundColor Red
    $errors++
}

Write-Host ""

# Check backend virtual environment
Write-Host "Checking backend virtual environment..." -ForegroundColor Yellow
$backendVenvPath = Join-Path $projectRoot "backend\venv"
$backendVenvActivate = Join-Path $backendVenvPath "Scripts\activate.bat"

if (Test-Path $backendVenvActivate) {
    Write-Host "  [OK] Backend venv found" -ForegroundColor Green
    
    # Check if uvicorn is installed
    $venvPython = Join-Path $backendVenvPath "Scripts\python.exe"
    if (Test-Path $venvPython) {
        $uvicornCheck = & $venvPython -c "import uvicorn; print('ok')" 2>&1
        if ($uvicornCheck -eq "ok") {
            Write-Host "  [OK] uvicorn installed" -ForegroundColor Green
        } else {
            Write-Host "  [WARNING] uvicorn not found" -ForegroundColor Yellow
            $warnings++
        }
    }
} else {
    Write-Host "  [ERROR] Backend venv not found" -ForegroundColor Red
    $errors++
}

Write-Host ""

# Check root .venv
Write-Host "Checking for root .venv..." -ForegroundColor Yellow
$rootVenvPath = Join-Path $projectRoot ".venv"
if (Test-Path $rootVenvPath) {
    Write-Host "  [WARNING] Root .venv found (will be ignored)" -ForegroundColor Yellow
    $warnings++
} else {
    Write-Host "  [OK] No root .venv found" -ForegroundColor Green
}

Write-Host ""

# Check Node.js installation
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
$nodeCheck = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Node.js found: $nodeCheck" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Node.js not found" -ForegroundColor Red
    $errors++
}

Write-Host ""

# Check frontend dependencies
Write-Host "Checking frontend dependencies..." -ForegroundColor Yellow
$frontendNodeModules = Join-Path $projectRoot "frontend_nextjs\node_modules"
if (Test-Path $frontendNodeModules) {
    Write-Host "  [OK] Frontend node_modules found" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] Frontend node_modules not found" -ForegroundColor Yellow
    $warnings++
}

Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "[OK] All checks passed! Environment is ready." -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the app:" -ForegroundColor Cyan
    Write-Host "  - Run: .\start_app.ps1" -ForegroundColor White
    Write-Host "  - Or use VS Code tasks" -ForegroundColor White
} else {
    if ($errors -gt 0) {
        Write-Host "[ERROR] $errors error(s) found. Please fix them." -ForegroundColor Red
    }
    if ($warnings -gt 0) {
        Write-Host "[WARNING] $warnings warning(s) found." -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "See START_HERE.md for troubleshooting." -ForegroundColor Yellow
}
