# PowerShell script for testing Flask server only
# filepath: test-flask-only.ps1

Write-Host "🧪 Testing Flask server locally (without Docker)..." -ForegroundColor Green

# Check if Python is installed
try {
    python --version | Out-Null
} catch {
    Write-Host "❌ Python not found. Please install Python 3.x" -ForegroundColor Red
    exit 1
}

# Check if Flask is installed
try {
    python -c "import flask" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "📦 Installing Flask..." -ForegroundColor Yellow
        pip install flask
    }
} catch {
    Write-Host "📦 Installing Flask..." -ForegroundColor Yellow
    pip install flask
}

# Set test environment variables
$env:APPLE_ID = "test@example.com"
$env:APPLE_PASSWORD = "test-password"

Write-Host "✅ Starting Flask server on http://localhost:8099" -ForegroundColor Green
Write-Host "📱 Open http://localhost:8099 in your browser" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start Flask
Set-Location hassio-icloud-backup
python setup_server.py
