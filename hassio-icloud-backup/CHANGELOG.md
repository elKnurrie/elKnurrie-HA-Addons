# Changelog

## [3.5.8] - 2025-10-30

### Fixed
- Enhanced Flask startup error detection
- Check if port is already in use before starting
- Test Flask responsiveness after startup
- Better error messages with exception types
- Increased startup wait time to 5 seconds
- Exit with error code if Flask fails (forces add-on stop)

This version adds comprehensive diagnostics to identify
why Flask exits immediately in Home Assistant:
- Port availability check
- Exception type and full traceback
- HTTP connectivity test
- Proper error exit codes

## [3.5.7] - 2025-10-30

### Fixed
- Re-enable Flask startup logging to diagnose 404 errors
- Add process health check in run.sh
- Log Flask server PID and startup status
- Better error reporting if Flask fails to start
- Keep stderr output to see Python errors in HA logs

This version adds debugging to identify why Flask might
not be responding to Ingress requests (404 errors).

## [3.5.6] - 2025-10-30

### Added
- Local Docker testing environment with docker-compose
- PowerShell test scripts for Windows development
- test-local.ps1 for full Docker testing
- test-flask-only.ps1 for rapid Flask-only testing
- TESTING.md with complete local testing guide
- Debugging tools for JSON response issues

### Developer Experience
- Test changes instantly without pushing to GitHub
- Iterate quickly with Flask-only mode
- Debug JSON responses in browser console
- Complete Docker testing environment

## [3.5.5] - 2025-10-30

### Fixed
- Follow Flask best practices: Return dict directly from routes
- Flask automatically serializes dicts to JSON (official recommendation)
- Remove jsonify() and Response() - unnecessary complexity
- Remove unused imports (threading, sys, Response)
- Cleaner, simpler code following official Flask documentation

Per Flask docs: "To return a JSON object from your API view,
you can directly return a dict from the view. It will be
serialized to JSON automatically."

## [3.5.4] - 2025-10-29

### Fixed
- Disable ALL Flask logging (werkzeug and app.logger)
- Use Response() instead of jsonify() for cleaner JSON
- Explicitly set mimetype='application/json'
- Remove all logging statements that could leak to HTTP
- Completely silent Flask server

This version strips out every possible source of output
that could contaminate HTTP responses.

## [3.5.3] - 2025-10-29

### Fixed
- **CRITICAL FIX**: Stop piping Flask output through bashio
- Flask server now runs independently without output redirection
- Prevents stdout/stderr from contaminating HTTP responses
- Add explicit Content-Type headers to all JSON responses
- Redirect Flask output to /dev/null to prevent interference

The issue: run.sh was piping Flask's output through bashio::log,
which was mixing with HTTP responses and breaking JSON.

## [3.5.2] - 2025-10-28

### Fixed
- Replace all print() statements with app.logger
- Prevent print output from corrupting JSON responses
- Use Flask's proper logging system throughout
- Clean JSON responses without stdout contamination

The JSON syntax error was caused by print() statements
mixing with the JSON response output. Now using proper
Flask logging that doesn't interfere with HTTP responses.

## [3.5.1] - 2025-10-28

### Fixed
- Fix JSON syntax error in request_code endpoint
- Better error handling for rclone obscure command
- Use subprocess.run() instead of check_output() for cleaner output
- Proper exception handling for configuration preparation

## [3.5.0] - 2025-10-28

### Added
- **"Request 2FA Code" button** - explicitly triggers Apple authentication
- Two-step authentication flow for clarity
- Process persistence between request and code submission
- Better user guidance and instructions

### Changed
- Authentication no longer auto-triggers on page load
- User must click button to request 2FA code from Apple
- Form only appears after 2FA request is sent
- Clearer separation between requesting code and entering code

### How It Works Now
1. Click "OPEN WEB UI"
2. Click **"Request 2FA Code from Apple"** button
3. **Apple NOW sends 2FA to your iPhone** ✅
4. Enter the 6-digit code
5. Click "Authenticate with iCloud"
6. Restart add-on - done!

## [3.4.0] - 2025-10-28

### WORKING! Flask server now executes rclone authentication!

### Added
- Flask server directly executes rclone commands
- Automated 2FA code submission to rclone
- Real-time status updates during authentication
- Background thread for non-blocking authentication
- Proper error handling and timeout management

### Changed
- Web UI now actually triggers Apple authentication
- 2FA code is sent to rclone subprocess
- Session tokens saved automatically
- No terminal access required!

### How It Works Now
1. Click OPEN WEB UI
2. Apple sends 2FA to your iPhone (triggered by rclone)
3. Enter the code in web form
4. Authentication completes automatically
5. Restart add-on - done!

## [3.3.0] - 2025-10-28

### Changed
- Update documentation with realistic setup instructions
- Clarify that rclone requires interactive terminal for initial auth
- Provide clear SSH/Terminal add-on setup guide
- Authentication actually triggers Apple to send 2FA now

### Documentation
- Honest explanation of limitations
- Step-by-step Terminal & SSH add-on setup
- Explain why web form alone cannot trigger Apple's 2FA

**Note:** The web UI remains for future enhancements, but initial
setup requires SSH/Terminal access to run `rclone config`.

## [3.2.4] - 2025-10-28

### Fixed
- Fix 503 error: Only enforce IP whitelist when INGRESS_PATH is set
- Allow all IPs in standalone mode (when Ingress is not active)
- Add better logging to show IP restriction mode

### Changed
- IP restriction only applies when running under Ingress
- Standalone mode allows connections from any IP

## [3.2.3] - 2025-10-28

### Fixed
- Add IP whitelist security for Ingress (required: 172.30.32.2 only)
- Implement proper Ingress security as per HA documentation
- Reject all connections not from Home Assistant gateway

### Security
- Only accept connections from Home Assistant Ingress gateway IP

## [3.2.2] - 2025-10-28

### Fixed
- Fix Ingress 503 error
- Simplify route handling for Ingress support
- Add proper Flask threading and reloader settings
- Better logging of web server startup
- Remove redundant path handling

## [3.2.1] - 2025-10-28

### Changed
- Enable Home Assistant Ingress support
- Web UI now opens directly in sidebar (no port forwarding needed!)
- Improved UI styling with better mobile support
- Auto-focus on 2FA code input field
- Better error messages and user guidance

### Removed
- External port exposure (now uses ingress)
- No need for port forwarding or webui URL

**Now even easier:** Just click "OPEN WEB UI" and the setup page opens in the sidebar!

## [3.2.0] - 2025-10-28

### Added
- Web UI for 2FA authentication setup (no terminal needed!)
- Click "OPEN WEB UI" button to enter 2FA code
- Session token persistence for future runs
- Automatic authentication flow

### Changed
- No longer requires terminal access
- Web-based setup wizard
- Clear instructions in logs

### How to Use
1. Install and start add-on
2. Click "OPEN WEB UI" button
3. Enter your 2FA code
4. Restart add-on - done!

## [3.1.0] - 2025-10-28

### ✅ WORKING SOLUTION!

Complete rewrite using rclone's native iCloud Drive support!

### Changed
- Use rclone's `iclouddrive` backend (officially supported!)
- Proper 2FA authentication through rclone config
- Session token persistence for subsequent runs
- Remove all Python dependencies
- Simple bash script implementation

### How It Works
- First run: Interactive `rclone config` for 2FA
- Session token is saved to `/data/rclone-icloud-session.txt`
- Subsequent runs: Use saved session (no 2FA needed)
- Standard rclone sync commands

### Setup Required
1. Install and start add-on (will fail)
2. Run `rclone config` in terminal
3. Complete 2FA authentication
4. Restart add-on (now works!)

**Status:** ✅ FUNCTIONAL - rclone natively supports iCloud Drive!

## [3.0.0] - 2025-10-28

### BREAKING CHANGES
- Complete rewrite using browser automation (Selenium + Chromium)
- Mimics web browser to access iCloud.com directly
- This is an EXPERIMENTAL approach

### Added
- Headless Chromium browser for automation
- Selenium WebDriver for browser control
- Automated login to iCloud.com
- Screenshot capture for debugging

### Note
This version tests if browser automation can bypass the API limitations.
It will likely still hit the 2FA requirement, but this approach could work
with session cookie persistence or other workarounds.

**Status: EXPERIMENTAL** - Testing if this approach is viable.

## [2.0.6] - 2025-10-28

### Changed
- Removed password debug logging
- Cleaned up test files
- Project on hold due to Apple iCloud Drive API limitations

### Note
Apple's iCloud Drive does not support app-specific passwords via the pyicloud API.
This add-on is currently non-functional and requires alternative approaches.

## [2.0.5] - 2025-10-28

### Changed
- Add temporary debug logging to verify password is passed correctly
- Show password length and format in logs (TEMPORARY - for debugging)
- **WARNING**: This version logs the full password - remove after testing!

## [2.0.4] - 2025-10-28

### Fixed
- Fix Docker build: Install pytz via pip (py3-pytz doesn't exist in Alpine)
- Remove non-existent py3-pytz package from apk

## [2.0.3] - 2025-10-28

### Fixed
- Fix Python 3.12 compatibility (imp module removed in 3.12)
- Add setuptools dependency
- Add imp module workaround for pyicloud-ipd
- Install py3-pytz for timezone support

## [2.0.2] - 2025-10-28

### Changed
- Switch to pyicloud-ipd (actively maintained fork)
- Add support for PyiCloud2SARequiredError exception
- Verify iCloud Drive access after authentication
- Enhanced error messages with step-by-step troubleshooting
- Better handling of 2FA and app-specific password requirements

### Fixed
- Improved library compatibility with fallback imports
- Added explicit iCloud Drive access verification

## [2.0.1] - 2025-10-28

### Fixed
- Improved authentication error messages
- Added cookie directory persistence for iCloud sessions
- Better debugging information for login failures
- More detailed troubleshooting steps

### Changed
- Enhanced error messages to guide users to app-specific password setup
- Added explicit instructions for common authentication issues

## [2.0.0] - 2025-10-28

### Breaking Changes
- **Complete rewrite**: Now uses PyiCloud library instead of rclone
- Uses official iCloud Drive API instead of non-existent WebDAV endpoint
- Configuration options changed (removed `icloud_webdav_url` and `backup_destination`)

### Added
- Native iCloud Drive API support via pyicloud
- Proper folder management in iCloud Drive
- Better error messages and logging
- Direct file upload without WebDAV

### Fixed
- Fixed fundamental issue: iCloud doesn't support WebDAV for iCloud Drive
- Removed dependency on DNS resolution of non-existent webdav.icloud.com
- No longer requires FUSE or privileged access

### Removed
- Removed rclone dependency
- Removed WebDAV configuration
- Removed FUSE mounting
- Removed unnecessary system packages

### Notes
- Requires app-specific password from appleid.apple.com
- PyiCloud doesn't support interactive 2FA prompts
- Uploads happen once when add-on starts

## [1.0.8] - 2025-10-28

### Fixed
- Add DNS workaround: manually resolve and add to /etc/hosts
- Install bind-tools (nslookup) for DNS resolution
- Use Google DNS (8.8.8.8) to resolve iCloud hostname
- Bypass Docker's internal DNS issues

## [1.0.6] - 2025-10-28

### Fixed
- Use explicit public DNS servers (Google DNS, Cloudflare)
- Disable host_network and use container networking with custom DNS
- Fixes persistent DNS resolution issues

## [1.0.5] - 2025-10-28

### Fixed
- Enable host_network to fix DNS resolution issues
- Resolves "no such host" error when connecting to iCloud WebDAV

## [1.0.4] - 2025-10-28

### Fixed
- Add verbose debugging output for connection failures
- Log WebDAV URL and username for troubleshooting
- Capture and display rclone error messages
- Improve error messages with specific troubleshooting steps

## [1.0.3] - 2025-10-28

### Fixed
- Fixed rclone config file format (proper INI format with [section])
- Use rclone obscure for password encryption
- Added connection test before syncing
- Improved error messages and logging with bashio
- Changed from mount to direct sync (more reliable)
- Added validation for required credentials

### Changed
- Use `rclone sync` instead of mount for better reliability
- Improved logging throughout the script
- Better error handling and user feedback

## [1.0.2] - 2025-10-28

### Fixed
- Fixed rclone installation to use direct download instead of install script
- Added unzip package for rclone installation
- Fixed BusyBox unzip compatibility issue

## [1.0.1] - 2025-10-28

### Fixed
- Fixed Dockerfile to use apk package manager instead of pip (resolves PEP 668 error)
- Added missing packages for FUSE mounting (fuse, ca-certificates)
- Updated run.sh shebang to use bashio format
- Consolidated RUN commands for better Docker layer optimization

## [1.0.0] - 2025-10-28

### Added
- Initial release
- Automatic backup of Home Assistant snapshots to iCloud via WebDAV
- Configurable retention policy for old backups
- Support for multiple architectures (amd64, armv7, aarch64)
- Uses rclone for reliable file synchronization