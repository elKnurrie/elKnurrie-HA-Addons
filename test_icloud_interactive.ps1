# iCloud Interactive Setup for rclone
# This handles the initial trust token creation

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "iCloud Interactive Authentication" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "This will set up rclone to connect to your iCloud Drive" -ForegroundColor Yellow
Write-Host "You'll need to enter a 2FA code when prompted" -ForegroundColor Yellow
Write-Host ""

# Get credentials
$username = Read-Host "Enter your Apple ID (email)"
$password = Read-Host "Enter your app-specific password (NOT your regular password)" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

if ([string]::IsNullOrWhiteSpace($username) -or [string]::IsNullOrWhiteSpace($passwordPlain)) {
    Write-Host "❌ Username and password are required" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setting up rclone config..." -ForegroundColor Cyan

# Create rclone config directory
$configDir = "$env:APPDATA\rclone"
if (!(Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

# Obscure the password
$obscuredPass = rclone obscure $passwordPlain

# Create basic config
$configContent = @"
[icloud]
type = iclouddrive
user = $username
pass = $obscuredPass
"@

$configPath = "$configDir\rclone.conf"
$configContent | Out-File -FilePath $configPath -Encoding ASCII -Force
Write-Host "✅ Config file created" -ForegroundColor Green

Write-Host ""
Write-Host "Now we need to establish the trust token..." -ForegroundColor Yellow
Write-Host "This will trigger a 2FA code to be sent to your devices" -ForegroundColor Yellow
Write-Host ""
Write-Host "Running: rclone config reconnect icloud:" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Run the reconnect command interactively
# This will prompt for 2FA code
& rclone config reconnect icloud:

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SUCCESS! Trust token established" -ForegroundColor Green
    Write-Host ""
    Write-Host "Testing the connection..." -ForegroundColor Cyan
    
    $testOutput = rclone lsd icloud: 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Connection test successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your iCloud Drive folders:" -ForegroundColor Cyan
        Write-Host $testOutput
        Write-Host ""
        Write-Host "🎉 You can now use this config in Home Assistant!" -ForegroundColor Green
        Write-Host ""
        Write-Host "The authentication tokens are stored in:" -ForegroundColor Yellow
        Write-Host "$configPath" -ForegroundColor White
    } else {
        Write-Host "⚠️  Connection test failed, but trust token may have been created" -ForegroundColor Yellow
        Write-Host "Error: $testOutput" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Failed to establish trust token" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  - Make sure you're using an APP-SPECIFIC password" -ForegroundColor Gray
    Write-Host "  - The 2FA code must be entered quickly (expires in ~60 seconds)" -ForegroundColor Gray
    Write-Host "  - Check your Apple ID settings at appleid.apple.com" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
