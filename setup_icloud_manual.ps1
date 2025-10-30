# iCloud rclone Configuration - INTERACTIVE
# This uses rclone config to properly set up iCloud with 2FA

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "iCloud rclone Interactive Setup" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "This will guide you through setting up iCloud Drive in rclone" -ForegroundColor Yellow
Write-Host ""

Write-Host "IMPORTANT: You need an APP-SPECIFIC password from Apple" -ForegroundColor Red
Write-Host "Generate one at: https://appleid.apple.com/account/manage" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

Write-Host "Starting rclone interactive configuration..." -ForegroundColor Cyan
Write-Host ""
Write-Host "When prompted:" -ForegroundColor Yellow
Write-Host "  1. Choose: n (new remote)" -ForegroundColor White
Write-Host "  2. Name: icloud" -ForegroundColor White
Write-Host "  3. Storage: Find and select 'iclouddrive'" -ForegroundColor White
Write-Host "  4. Enter your Apple ID email" -ForegroundColor White
Write-Host "  5. Enter your APP-SPECIFIC password" -ForegroundColor White
Write-Host "  6. Wait for 2FA code on your iPhone/iPad" -ForegroundColor White
Write-Host "  7. Enter the 6-digit code when prompted" -ForegroundColor White
Write-Host "  8. Confirm and quit" -ForegroundColor White
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Run rclone config interactively
rclone config

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "Testing the connection..." -ForegroundColor Cyan
    Write-Host ""
    
    $testOutput = rclone lsd icloud: 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SUCCESS! iCloud Drive is connected!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your iCloud Drive folders:" -ForegroundColor Cyan
        Write-Host $testOutput -ForegroundColor White
        Write-Host ""
        Write-Host "🎉 Configuration complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "The config is saved at:" -ForegroundColor Yellow
        Write-Host "$env:APPDATA\rclone\rclone.conf" -ForegroundColor White
        Write-Host ""
        Write-Host "You can now use this in your Home Assistant add-on!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Connection test failed" -ForegroundColor Yellow
        Write-Host "Output: $testOutput" -ForegroundColor Red
        Write-Host ""
        Write-Host "The configuration may have been saved, but couldn't connect" -ForegroundColor Yellow
        Write-Host "Try running: rclone lsd icloud:" -ForegroundColor Cyan
    }
} else {
    Write-Host "Configuration was not completed or encountered an error" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
