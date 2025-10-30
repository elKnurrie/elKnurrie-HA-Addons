# PowerShell script for local testing
# filepath: test-local.ps1

Write-Host "🚀 Starting local iCloud Backup add-on test environment..." -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".devcontainer\.env")) {
    Write-Host "⚠️  No .env file found. Creating from example..." -ForegroundColor Yellow
    Copy-Item ".devcontainer\.env.example" ".devcontainer\.env"
    Write-Host "📝 Please edit .devcontainer\.env with your Apple ID credentials" -ForegroundColor Yellow
    Write-Host "   Then run this script again." -ForegroundColor Yellow
    exit 1
}

# Create test directories
Write-Host "📁 Creating test directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path ".devcontainer\test-data" | Out-Null
New-Item -ItemType Directory -Force -Path ".devcontainer\test-backups" | Out-Null

# Create a test backup file
Write-Host "📦 Creating test backup file..." -ForegroundColor Cyan
$date = Get-Date -Format "yyyyMMdd"
"Test backup created at $(Get-Date)" | Out-File -FilePath ".devcontainer\test-backups\test-backup-$date.tar"

# Build and start the container
Write-Host "🐳 Building Docker container..." -ForegroundColor Cyan
Set-Location .devcontainer
docker-compose -f docker-compose.test.yml up --build

# Cleanup
Write-Host "🧹 Cleaning up..." -ForegroundColor Cyan
docker-compose -f docker-compose.test.yml down
Set-Location ..
