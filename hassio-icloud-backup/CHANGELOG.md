# Changelog

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