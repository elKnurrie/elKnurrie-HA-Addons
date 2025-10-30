# Local Testing Guide

This guide explains how to test the iCloud Backup add-on locally on Windows without deploying to Home Assistant.

## Prerequisites

- Docker Desktop for Windows (installed and running)
- PowerShell
- Python 3.x (for Flask-only testing)

## Quick Start

### Option 1: Full Docker Test (Recommended)

Test the complete add-on including all dependencies:

1. **Set up credentials:**
   ```powershell
   # Copy the example file
   Copy-Item .devcontainer\.env.example .devcontainer\.env
   
   # Edit with your credentials (use Notepad or your favorite editor)
   notepad .devcontainer\.env
   ```

2. **Run the test:**
   ```powershell
   .\test-local.ps1
   ```

3. **Open browser:**
   Navigate to http://localhost:8099

### Option 2: Flask Server Only (Fast Iteration)

Test just the Flask web interface without Docker (fastest for UI testing):

```powershell
.\test-flask-only.ps1
```

Then open http://localhost:8099 in your browser.

### Option 3: Manual Docker Commands

For complete control:

```powershell
# Build the image
cd hassio-icloud-backup
docker build -t icloud-backup-test .

# Run with your configuration
docker run -it --rm `
  -p 8099:8099 `
  -e APPLE_ID="your-email@example.com" `
  -e APPLE_PASSWORD="your-app-password" `
  -v ${PWD}/test-data:/data `
  -v ${PWD}/test-backups:/backup:ro `
  icloud-backup-test
```

## Development Workflow

1. **Make code changes** in `hassio-icloud-backup/`
2. **Test locally** using Option 2 (fastest) or Option 1 (complete test)
3. **Check browser console** (F12) for any errors
4. **Check PowerShell output** for server logs
5. **Iterate** - no need to push to GitHub!

## Debugging the JSON Error

To debug the JSON parsing error you're experiencing:

### 1. Test with Flask Only (Fastest)
```powershell
.\test-flask-only.ps1
```

### 2. Open Browser Developer Tools
- Press F12 in your browser
- Go to Console tab
- Click "Request 2FA Code" button
- Look for the console.log output showing the raw response

### 3. Check for Issues
The error `SyntaxError: Unexpected non-whitespace character after JSON at position 3` means there's extra content before or after the JSON.

Look for:
- Extra whitespace or newlines before `{`
- Text output before the JSON (like Flask startup messages)
- Multiple JSON objects instead of one

### 4. Test the Endpoint Directly
```powershell
# Test in PowerShell
Invoke-WebRequest -Uri http://localhost:8099/request_code -Method POST | Select-Object -ExpandProperty Content

# Should return clean JSON like:
# {"success": true, "message": "..."}
```

## Common Issues

### Port 8099 Already in Use
```powershell
# Find the process using the port
Get-NetTCPConnection -LocalPort 8099 | Select-Object OwningProcess
# Kill it
Stop-Process -Id <ProcessId>
```

### Docker Not Running
```powershell
# Check if Docker is running
docker ps
# If error, start Docker Desktop
```

### Python Not Found
```powershell
# Check Python installation
python --version
# If not installed, download from https://python.org
```

## Testing Checklist

- [ ] Flask server starts without errors
- [ ] Web UI loads at http://localhost:8099
- [ ] Can click "Request 2FA Code" button  
- [ ] Browser console shows clean JSON response
- [ ] No syntax errors in console
- [ ] Can enter 2FA code (if you have one)
- [ ] Check server output for any print statements

## Cleanup

Stop Docker containers:
```powershell
cd .devcontainer
docker-compose -f docker-compose.test.yml down -v
cd ..
```

## Next Steps

Once you identify the issue with local testing:
1. Fix the code
2. Test again locally (instant feedback!)
3. Commit and push to GitHub
4. Update your Home Assistant add-on

## Quick Commands Reference

```powershell
# Test Flask only (fastest)
.\test-flask-only.ps1

# Test with Docker (complete)
.\test-local.ps1

# View Docker logs
docker logs icloud-backup-test

# Stop everything
docker stop icloud-backup-test

# Clean rebuild
docker build --no-cache -t icloud-backup-test .\hassio-icloud-backup\
```
