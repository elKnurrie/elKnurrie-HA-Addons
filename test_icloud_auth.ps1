# iCloud Authentication Test Script for PowerShell
# This will help debug why 2FA codes aren't being received

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "iCloud Authentication Debug Tool" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Get credentials
$username = Read-Host "Enter your Apple ID (email)"
$password = Read-Host "Enter your Apple ID password" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

if ([string]::IsNullOrWhiteSpace($username) -or [string]::IsNullOrWhiteSpace($passwordPlain)) {
    Write-Host "❌ Username and password are required" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Testing rclone connection to iCloud..." -ForegroundColor Yellow
Write-Host "-" * 60

# Create rclone config directory
$configDir = "$env:APPDATA\rclone"
if (!(Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

# Obscure the password using rclone
Write-Host ""
Write-Host "1. Obscuring password with rclone..." -ForegroundColor Cyan
try {
    $obscuredPass = rclone obscure $passwordPlain
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Password obscured" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Failed to obscure password" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ rclone not found. Please restart PowerShell after installing rclone" -ForegroundColor Red
    Write-Host "   Or download from: https://rclone.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create rclone config
Write-Host ""
Write-Host "2. Creating rclone config..." -ForegroundColor Cyan
$configContent = @"
[icloud]
type = iclouddrive
user = $username
pass = $obscuredPass
"@

$configPath = "$configDir\rclone.conf"
$configContent | Out-File -FilePath $configPath -Encoding ASCII -Force
Write-Host "   ✅ Config written to $configPath" -ForegroundColor Green

# Try to connect to iCloud
Write-Host ""
Write-Host "3. Attempting to connect to iCloud Drive..." -ForegroundColor Cyan
Write-Host "   This should trigger Apple to send a 2FA code to your devices" -ForegroundColor Yellow
Write-Host "   Watch your iPhone/iPad for a notification!" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Starting rclone connection in verbose mode..." -ForegroundColor Cyan
Write-Host "   " + ("=" * 56)
Write-Host ""

# Run rclone and capture output
try {
    Write-Host "   Press Ctrl+C to cancel if nothing happens after 30 seconds" -ForegroundColor Gray
    Write-Host ""
    
    # Start rclone process
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "rclone"
    $psi.Arguments = "lsd icloud: --verbose"
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.RedirectStandardInput = $true
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    $process.Start() | Out-Null
    
    Write-Host "   [rclone process started, reading output...]" -ForegroundColor Gray
    Write-Host ""
    
    # Read output
    $hasOutput = $false
    $has2FAPrompt = $false
    $outputLines = @()
    
    while (!$process.HasExited) {
        $line = $process.StandardOutput.ReadLine()
        if ($line) {
            $hasOutput = $true
            $outputLines += $line
            Write-Host "   [rclone] $line" -ForegroundColor Gray
            
            # Check for 2FA-related messages
            if ($line -match '2fa|verification|code|trusted') {
                $has2FAPrompt = $true
                Write-Host ""
                Write-Host "   ⚠️  2FA PROMPT DETECTED! Check your iPhone/iPad!" -ForegroundColor Yellow
                Write-Host ""
            }
        }
        
        # Also check stderr
        if (!$process.StandardError.EndOfStream) {
            $errLine = $process.StandardError.ReadLine()
            if ($errLine) {
                $hasOutput = $true
                $outputLines += $errLine
                Write-Host "   [rclone] $errLine" -ForegroundColor Red
                
                if ($errLine -match '2fa|verification|code|trusted') {
                    $has2FAPrompt = $true
                    Write-Host ""
                    Write-Host "   ⚠️  2FA PROMPT DETECTED! Check your iPhone/iPad!" -ForegroundColor Yellow
                    Write-Host ""
                }
            }
        }
        
        Start-Sleep -Milliseconds 100
    }
    
    Write-Host ""
    Write-Host "   " + ("=" * 56)
    Write-Host ""
    
    # Analyze results
    $fullOutput = $outputLines -join " "
    
    if ($has2FAPrompt) {
        Write-Host "✅ 2FA code prompt was detected!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Did you receive a 2FA code on your iPhone/iPad?" -ForegroundColor Yellow
        $receivedCode = Read-Host "Enter the 6-digit code (or press Enter to skip)"
        
        if ($receivedCode -and $receivedCode.Length -eq 6) {
            Write-Host ""
            Write-Host "To test the code, run this command in the terminal where rclone is waiting:" -ForegroundColor Cyan
            Write-Host "rclone lsd icloud:" -ForegroundColor White
            Write-Host "Then enter: $receivedCode" -ForegroundColor White
        }
    } elseif ($fullOutput -match 'error|failed') {
        Write-Host "❌ Errors detected in rclone output" -ForegroundColor Red
        Write-Host ""
        Write-Host "Common issues:" -ForegroundColor Yellow
        Write-Host "  - Incorrect Apple ID or password" -ForegroundColor Gray
        Write-Host "  - App-specific password required (if 2FA already enabled on your Apple account)" -ForegroundColor Gray
        Write-Host "  - Generate one at: https://appleid.apple.com/account/manage" -ForegroundColor Cyan
        Write-Host "  - Account locked or security issues" -ForegroundColor Gray
    } elseif (!$hasOutput) {
        Write-Host "⚠️  No output from rclone - the process may have failed silently" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Try running manually:" -ForegroundColor Cyan
        Write-Host "rclone lsd icloud: --verbose" -ForegroundColor White
    } else {
        Write-Host "⚠️  No clear 2FA prompts detected" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "This could mean:" -ForegroundColor Yellow
        Write-Host "  1. You need an app-specific password instead of your regular password" -ForegroundColor Gray
        Write-Host "     Create one at: https://appleid.apple.com/account/manage" -ForegroundColor Cyan
        Write-Host "  2. Your account doesn't have 2FA enabled yet" -ForegroundColor Gray
        Write-Host "  3. The credentials are incorrect" -ForegroundColor Gray
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Debug session complete" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 TIP: If you have 2FA enabled on your Apple account, you MUST use an" -ForegroundColor Yellow
Write-Host "   app-specific password instead of your regular Apple ID password." -ForegroundColor Yellow
Write-Host "   Generate one at: https://appleid.apple.com/account/manage" -ForegroundColor Cyan
