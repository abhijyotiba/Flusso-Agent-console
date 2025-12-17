# Quick Start Script for Agent Assist Console (Windows PowerShell)
# Run this script to set up and start the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agent Assist Console - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.([0-9]+)") {
    $minorVersion = [int]$Matches[1]
    if ($minorVersion -ge 11) {
        Write-Host "✓ Python version OK: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Python 3.11+ required. Found: $pythonVersion" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ Python not found or version check failed" -ForegroundColor Red
    exit 1
}

# Check if .env exists
Write-Host ""
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Write-Host "⚠ .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host "⚠ IMPORTANT: Edit .env and add your GOOGLE_API_KEY" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter after you've added your API key to .env"
} else {
    Write-Host "✓ .env file exists" -ForegroundColor Green
}

# Check if virtual environment exists
Write-Host ""
Write-Host "Setting up virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
Set-Location "server"
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Set-Location ".."

# Check data files
Write-Host ""
Write-Host "Checking data files..." -ForegroundColor Yellow
if ((Test-Path "server/data/Product-2025-11-12.xlsx") -and (Test-Path "server/data/metadata_manifest.json")) {
    Write-Host "✓ Data files found" -ForegroundColor Green
} else {
    Write-Host "⚠ Data files not found. Make sure Product-2025-11-12.xlsx and metadata_manifest.json exist in server/data/" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Starting the application..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend will start on:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend will serve at: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the servers" -ForegroundColor Yellow
Write-Host ""

# Start backend in background job
Write-Host "Starting backend server..." -ForegroundColor Yellow
$backend = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & .\venv\Scripts\Activate.ps1
    Set-Location "server"
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in background job
Write-Host "Starting frontend server..." -ForegroundColor Yellow
$frontend = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location "client"
    python -m http.server 3000
}

Write-Host ""
Write-Host "✓ Servers started!" -ForegroundColor Green
Write-Host ""
Write-Host "Open your browser and navigate to:" -ForegroundColor Cyan
Write-Host "  http://localhost:3000" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host ""
Write-Host "API Documentation available at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

# Monitor jobs
try {
    while ($true) {
        # Check if jobs are still running
        if ((Get-Job -Id $backend.Id).State -ne "Running" -or (Get-Job -Id $frontend.Id).State -ne "Running") {
            Write-Host ""
            Write-Host "⚠ One or more servers stopped unexpectedly" -ForegroundColor Red
            break
        }
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host ""
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $backend, $frontend
    Remove-Job -Job $backend, $frontend
    Write-Host "✓ Servers stopped" -ForegroundColor Green
}
