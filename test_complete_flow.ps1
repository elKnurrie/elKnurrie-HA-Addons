# Complete local test simulating the add-on's 2FA flow
# This mimics exactly what happens in Home Assistant

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Complete iCloud 2FA Flow Test (Simulating HA Add-on)" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

Write-Host "This test simulates the EXACT flow that happens in Home Assistant:" -ForegroundColor Yellow
Write-Host "  1. Create rclone config with app-specific password" -ForegroundColor Gray
Write-Host "  2. Trigger trust token request (sends 2FA code)" -ForegroundColor Gray
Write-Host "  3. Submit 2FA code" -ForegroundColor Gray
Write-Host "  4. Verify trust tokens are saved" -ForegroundColor Gray
Write-Host "  5. Test automatic access (no more 2FA!)" -ForegroundColor Gray
Write-Host ""

# Get credentials
$username = Read-Host "Enter your Apple ID (email)"
$password = Read-Host "Enter your app-specific password" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

if ([string]::IsNullOrWhiteSpace($username) -or [string]::IsNullOrWhiteSpace($passwordPlain)) {
    Write-Host "❌ Username and password required" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "━" * 70 -ForegroundColor Cyan
Write-Host "STEP 1: Creating rclone config" -ForegroundColor Cyan
Write-Host "━" * 70 -ForegroundColor Cyan

# Obscure password
Write-Host "Obscuring password..." -ForegroundColor Gray
$obscuredPass = rclone obscure $passwordPlain
Write-Host "✅ Password obscured" -ForegroundColor Green

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
Write-Host "✅ Config created at: $configPath" -ForegroundColor Green

Write-Host ""
Write-Host "━" * 70 -ForegroundColor Cyan
Write-Host "STEP 2: Requesting trust tokens (triggers 2FA)" -ForegroundColor Cyan
Write-Host "━" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  WATCH YOUR IPHONE/IPAD - 2FA CODE WILL BE SENT NOW!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Starting rclone process that will request trust tokens..." -ForegroundColor Gray

# Start rclone process
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

Write-Host "Process started, waiting for 2FA prompt..." -ForegroundColor Gray
Write-Host ""

# Read output for up to 15 seconds or until we detect 2FA
$detectedPrompt = $false
$outputText = ""
$timeout = 15
$elapsed = 0

while ($elapsed -lt $timeout -and !$process.HasExited) {
    # Read stdout
    if (!$process.StandardOutput.EndOfStream) {
        $line = $process.StandardOutput.ReadLine()
        if ($line) {
            $outputText += "$line`n"
            Write-Host "  [rclone] $line" -ForegroundColor Gray
            
            if ($line -match 'enter.+code|verification.+code|trust.+token|2fa') {
                $detectedPrompt = $true
                Write-Host ""
                Write-Host "  🔔 2FA PROMPT DETECTED!" -ForegroundColor Yellow
                Write-Host ""
                break
            }
        }
    }
    
    # Read stderr
    if (!$process.StandardError.EndOfStream) {
        $line = $process.StandardError.ReadLine()
        if ($line) {
            $outputText += "$line`n"
            Write-Host "  [rclone] $line" -ForegroundColor Yellow
            
            if ($line -match 'enter.+code|verification.+code|trust.+token|2fa') {
                $detectedPrompt = $true
                Write-Host ""
                Write-Host "  🔔 2FA PROMPT DETECTED!" -ForegroundColor Yellow
                Write-Host ""
                break
            }
        }
    }
    
    Start-Sleep -Milliseconds 500
    $elapsed++
}

Write-Host ""
Write-Host "━" * 70 -ForegroundColor Cyan
Write-Host "STEP 3: Submit 2FA code" -ForegroundColor Cyan
Write-Host "━" * 70 -ForegroundColor Cyan
Write-Host ""

if ($outputText -match 'trust.?token') {
    Write-Host "✅ Trust token request detected!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Did you receive a 6-digit code on your iPhone/iPad?" -ForegroundColor Cyan
    $code = Read-Host "Enter the code"
    
    if ($code -and $code.Length -eq 6 -and $code -match '^\d+$') {
        Write-Host ""
        Write-Host "Submitting code '$code' to rclone..." -ForegroundColor Cyan
        
        # Send code to rclone
        $process.StandardInput.WriteLine($code)
        $process.StandardInput.Flush()
        
        # Wait for process to complete
        Write-Host "Waiting for rclone to process..." -ForegroundColor Gray
        
        $completed = $false
        $waitTime = 0
        while ($waitTime -lt 30) {
            if ($process.HasExited) {
                $completed = $true
                break
            }
            
            # Keep reading output
            while (!$process.StandardOutput.EndOfStream) {
                $line = $process.StandardOutput.ReadLine()
                if ($line) {
                    Write-Host "  [rclone] $line" -ForegroundColor Gray
                }
            }
            
            Start-Sleep -Seconds 1
            $waitTime++
        }
        
        if (!$completed) {
            Write-Host "  Timeout waiting for rclone, stopping process..." -ForegroundColor Yellow
            $process.Kill()
        }
        
        Write-Host ""
        Write-Host "━" * 70 -ForegroundColor Cyan
        Write-Host "STEP 4: Verifying trust tokens saved" -ForegroundColor Cyan
        Write-Host "━" * 70 -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Testing if authentication worked..." -ForegroundColor Cyan
        
        # Test with a fresh rclone command
        Start-Sleep -Seconds 2
        $testOutput = rclone lsd icloud: 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "🎉 SUCCESS! Trust tokens are saved!" -ForegroundColor Green
            Write-Host ""
            Write-Host "━" * 70 -ForegroundColor Cyan
            Write-Host "STEP 5: Testing automatic access (no 2FA!)" -ForegroundColor Cyan
            Write-Host "━" * 70 -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Your iCloud Drive folders:" -ForegroundColor Cyan
            Write-Host $testOutput -ForegroundColor White
            Write-Host ""
            Write-Host "━" * 70 -ForegroundColor Green
            Write-Host "✅ COMPLETE SUCCESS!" -ForegroundColor Green
            Write-Host "━" * 70 -ForegroundColor Green
            Write-Host ""
            Write-Host "Trust tokens are now saved in:" -ForegroundColor Yellow
            Write-Host "  $configPath" -ForegroundColor White
            Write-Host ""
            Write-Host "Future rclone commands will work automatically without 2FA!" -ForegroundColor Green
            Write-Host ""
            Write-Host "This is exactly what will happen in Home Assistant:" -ForegroundColor Cyan
            Write-Host "  1. You do 2FA once ✅" -ForegroundColor Gray
            Write-Host "  2. Trust tokens saved ✅" -ForegroundColor Gray
            Write-Host "  3. Automatic backups forever ✅" -ForegroundColor Gray
            Write-Host ""
        } else {
            Write-Host ""
            Write-Host "❌ Authentication may have failed" -ForegroundColor Red
            Write-Host ""
            Write-Host "Output:" -ForegroundColor Yellow
            Write-Host $testOutput -ForegroundColor Gray
            Write-Host ""
            Write-Host "Common issues:" -ForegroundColor Yellow
            Write-Host "  - Code entered too slowly (they expire quickly)" -ForegroundColor Gray
            Write-Host "  - Incorrect code" -ForegroundColor Gray
            Write-Host "  - Network issues" -ForegroundColor Gray
            Write-Host ""
            Write-Host "Try running the test again!" -ForegroundColor Cyan
        }
        
    } else {
        Write-Host "❌ Invalid code format (must be 6 digits)" -ForegroundColor Red
        if (!$process.HasExited) {
            $process.Kill()
        }
    }
} else {
    Write-Host "❌ No trust token request detected" -ForegroundColor Red
    Write-Host ""
    Write-Host "Output received:" -ForegroundColor Yellow
    Write-Host $outputText -ForegroundColor Gray
    Write-Host ""
    Write-Host "This might indicate:" -ForegroundColor Yellow
    Write-Host "  - Network connectivity issues" -ForegroundColor Gray
    Write-Host "  - Incorrect app-specific password" -ForegroundColor Gray
    Write-Host "  - Apple account issues" -ForegroundColor Gray
    
    if (!$process.HasExited) {
        $process.Kill()
    }
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Test Complete" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
