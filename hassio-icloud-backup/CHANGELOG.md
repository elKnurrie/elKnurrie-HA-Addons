# Changelog

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