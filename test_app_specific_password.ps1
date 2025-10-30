# Simple test to see if app-specific password works
# This will try to authenticate and show what happens

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Testing App-Specific Password Authentication" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$username = Read-Host "Enter your Apple ID (email)"
$password = Read-Host "Enter your app-specific password" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

Write-Host ""
Write-Host "Creating config..." -ForegroundColor Cyan

# Obscure password
$obscuredPass = rclone obscure $passwordPlain

# Create config
$configDir = "$env:APPDATA\rclone"
if (!(Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$configContent = @"
[icloud]
type = iclouddrive
apple_id = $username
password = $obscuredPass
"@

$configPath = "$configDir\rclone.conf"
$configContent | Out-File -FilePath $configPath -Encoding ASCII -Force
Write-Host "✅ Config created" -ForegroundColor Green

Write-Host ""
Write-Host "Testing authentication..." -ForegroundColor Cyan
Write-Host "Running: rclone about icloud:" -ForegroundColor Gray
Write-Host ""

# Use 'rclone about' to test auth without listing files
$output = rclone about icloud: -vv 2>&1 | Out-String

Write-Host $output

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

if ($output -match 'session.+token|trust.+token|2fa|verification') {
    Write-Host "⚠️  IMPORTANT FINDING:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "rclone's iCloud backend appears to require 'trust tokens' even" -ForegroundColor Yellow
    Write-Host "with app-specific passwords. This is a limitation of how Apple's" -ForegroundColor Yellow
    Write-Host "iCloud Drive API works." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "The app-specific password bypasses 2FA for AUTHENTICATION," -ForegroundColor Cyan
    Write-Host "but iCloud Drive access still requires device trust tokens." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This means rclone MUST perform an initial 2FA handshake to" -ForegroundColor Yellow
    Write-Host "establish trust, even with an app-specific password." -ForegroundColor Yellow
} elseif ($output -match 'Total:|Used:|Free:') {
    Write-Host "✅ SUCCESS! App-specific password works without 2FA!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your iCloud Drive stats:" -ForegroundColor Cyan
    Write-Host $output | Select-String "Total:|Used:|Free:" -ForegroundColor White
} else {
    Write-Host "⚠️  Unclear result - check output above" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
