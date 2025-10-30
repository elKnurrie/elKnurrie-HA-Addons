# Test rclone config create + lsf method for 2FA
# This is the correct sequence for iCloud authentication

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Testing: rclone config create + lsf for 2FA" -ForegroundColor Green  
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$username = Read-Host "Enter your Apple ID (email)"
$password = Read-Host "Enter your app-specific password" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

if ([string]::IsNullOrWhiteSpace($username) -or [string]::IsNullOrWhiteSpace($passwordPlain)) {
    Write-Host "❌ Username and password required" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 1: Obscuring password with rclone..." -ForegroundColor Cyan
Write-Host ""

try {
    $obscuredPass = rclone obscure $passwordPlain
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Password obscured" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to obscure password" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Creating rclone config with manual file..." -ForegroundColor Cyan
Write-Host ""

# Create config manually since config create doesn't support 2FA interactively
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
Write-Host "✅ Config file created at $configPath" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Attempting to list iCloud files (this triggers 2FA)..." -ForegroundColor Cyan
Write-Host "Command: rclone lsf icloud: --max-depth 1 -vv" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  WATCH YOUR IPHONE/IPAD FOR THE 2FA CODE!" -ForegroundColor Yellow
Write-Host ""

# Start the lsf process
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "rclone"
$psi.Arguments = "lsf icloud: --max-depth 1 -vv"
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.RedirectStandardInput = $true

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $psi
$process.Start() | Out-Null

Write-Host "Reading rclone output..." -ForegroundColor Gray
Write-Host ""

$hasOutput = $false
$has2FAPrompt = $false
$outputText = ""

# Read output for up to 20 seconds
$timeout = 20
$elapsed = 0

while ($elapsed -lt $timeout -and !$process.HasExited) {
    # Read stdout
    while (!$process.StandardOutput.EndOfStream) {
        $line = $process.StandardOutput.ReadLine()
        if ($line) {
            $hasOutput = $true
            $outputText += "$line`n"
            Write-Host "  [rclone] $line" -ForegroundColor Gray
            
            if ($line -match '2fa|verification|code|enter') {
                $has2FAPrompt = $true
                Write-Host ""
                Write-Host "  🔔 2FA PROMPT DETECTED!" -ForegroundColor Yellow
                Write-Host ""
            }
        }
    }
    
    # Read stderr
    while (!$process.StandardError.EndOfStream) {
        $line = $process.StandardError.ReadLine()
        if ($line) {
            $hasOutput = $true
            $outputText += "$line`n"
            Write-Host "  [rclone] $line" -ForegroundColor Yellow
            
            if ($line -match '2fa|verification|code|enter') {
                $has2FAPrompt = $true
                Write-Host ""
                Write-Host "  🔔 2FA PROMPT DETECTED!" -ForegroundColor Yellow
                Write-Host ""
            }
        }
    }
    
    Start-Sleep -Milliseconds 500
    $elapsed++
}

Write-Host ""

if ($has2FAPrompt) {
    Write-Host "✅ 2FA CODE WAS REQUESTED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Did you receive a 6-digit code on your iPhone/iPad?" -ForegroundColor Cyan
    $code = Read-Host "Enter the code (or press Enter to skip)"
    
    if ($code -and $code.Length -eq 6) {
        Write-Host "Sending code '$code' to rclone..." -ForegroundColor Cyan
        $process.StandardInput.WriteLine($code)
        $process.StandardInput.Flush()
        
        # Wait for result
        Start-Sleep -Seconds 5
        
        if (!$process.HasExited) {
            $process.Kill()
        }
        
        Write-Host "Testing if authentication worked..." -ForegroundColor Cyan
        $testOutput = rclone lsd icloud: 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "🎉 SUCCESS! iCloud Drive is now authenticated!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Your folders:" -ForegroundColor Cyan
            Write-Host $testOutput -ForegroundColor White
        } else {
            Write-Host "❌ Authentication may have failed" -ForegroundColor Red
            Write-Host $testOutput -ForegroundColor Gray
        }
    }
} elseif ($outputText -match 'trust token') {
    Write-Host "⚠️  Trust token error detected" -ForegroundColor Yellow
    Write-Host "This means 2FA wasn't triggered properly" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  No clear 2FA prompt detected" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Output received:" -ForegroundColor Gray
    Write-Host $outputText -ForegroundColor Gray
}

if (!$process.HasExited) {
    $process.Kill()
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Test complete" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
