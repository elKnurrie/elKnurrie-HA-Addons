# Test iCloud with REAL Apple ID password (not app-specific)
# This is the CORRECT way per rclone documentation

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "iCloud Drive Authentication Test - CORRECT METHOD" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  CRITICAL REQUIREMENTS:" -ForegroundColor Red
Write-Host ""
Write-Host "Before running this test, verify on your iPhone/iPad:" -ForegroundColor Yellow
Write-Host "  1. Settings → [Your Name] → iCloud → Advanced Data Protection = OFF" -ForegroundColor White
Write-Host "  2. Settings → [Your Name] → iCloud → Access iCloud Data on the Web = ON" -ForegroundColor White
Write-Host ""

$confirmed = Read-Host "Have you verified these settings? (yes/no)"
if ($confirmed -ne "yes") {
    Write-Host ""
    Write-Host "Please configure your iCloud settings first, then run this test again." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "IMPORTANT: Use your REAL Apple ID password" -ForegroundColor Red
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "❌ DO NOT use an app-specific password" -ForegroundColor Red
Write-Host "✅ Use the SAME password you use to log into your iPhone/Mac/iPad" -ForegroundColor Green
Write-Host ""

$username = Read-Host "Enter your Apple ID (email)"
$password = Read-Host "Enter your REAL Apple ID password (not app-specific!)" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

Write-Host ""
Write-Host "Creating rclone config..." -ForegroundColor Cyan

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
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Testing authentication..." -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  WATCH YOUR IPHONE/IPAD FOR 2FA CODE!" -ForegroundColor Yellow
Write-Host ""

# Start rclone
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

Write-Host "Waiting for 2FA prompt..." -ForegroundColor Gray
Write-Host ""

$hasPrompt = $false
$output = ""
$elapsed = 0

while ($elapsed -lt 20 -and !$process.HasExited) {
    if (!$process.StandardOutput.EndOfStream) {
        $line = $process.StandardOutput.ReadLine()
        if ($line) {
            $output += "$line`n"
            Write-Host "  [rclone] $line" -ForegroundColor Gray
            
            if ($line -match 'code|token|2fa|verification') {
                $hasPrompt = $true
            }
        }
    }
    
    if (!$process.StandardError.EndOfStream) {
        $line = $process.StandardError.ReadLine()
        if ($line) {
            $output += "$line`n"
            Write-Host "  [rclone] $line" -ForegroundColor Yellow
            
            if ($line -match 'code|token|2fa|verification') {
                $hasPrompt = $true
            }
        }
    }
    
    Start-Sleep -Milliseconds 500
    $elapsed++
}

Write-Host ""

if ($hasPrompt -or $output -match 'trust') {
    Write-Host "✅ 2FA prompt detected!" -ForegroundColor Green
    Write-Host ""
    $code = Read-Host "Enter the 6-digit code from your iPhone/iPad"
    
    if ($code -and $code.Length -eq 6) {
        Write-Host "Submitting code..." -ForegroundColor Cyan
        $process.StandardInput.WriteLine($code)
        $process.StandardInput.Flush()
        
        Start-Sleep -Seconds 5
        
        if (!$process.HasExited) {
            $process.Kill()
        }
        
        Write-Host ""
        Write-Host "Testing if authentication worked..." -ForegroundColor Cyan
        $testOutput = rclone lsd icloud: 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "🎉 SUCCESS!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Your iCloud Drive folders:" -ForegroundColor Cyan
            Write-Host $testOutput -ForegroundColor White
            Write-Host ""
            Write-Host "=" * 70 -ForegroundColor Green
            Write-Host "✅ AUTHENTICATION SUCCESSFUL!" -ForegroundColor Green
            Write-Host "=" * 70 -ForegroundColor Green
            Write-Host ""
            Write-Host "Trust tokens saved. Future commands will work without 2FA!" -ForegroundColor Green
            Write-Host ""
            Write-Host "⚠️  REMEMBER: Tokens expire after 30 days" -ForegroundColor Yellow
            Write-Host "You'll need to re-authenticate monthly" -ForegroundColor Yellow
            Write-Host ""
        } else {
            Write-Host ""
            Write-Host "❌ Authentication failed" -ForegroundColor Red
            Write-Host $testOutput -ForegroundColor Red
        }
    }
} else {
    Write-Host "❌ No 2FA prompt detected" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  - Advanced Data Protection is still enabled" -ForegroundColor Gray
    Write-Host "  - Access iCloud Data on the Web is disabled" -ForegroundColor Gray
    Write-Host "  - Incorrect password (must be real Apple ID password, not app-specific)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Full output:" -ForegroundColor Yellow
    Write-Host $output -ForegroundColor Gray
    
    if (!$process.HasExited) {
        $process.Kill()
    }
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
