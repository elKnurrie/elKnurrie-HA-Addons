# Changelog

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