# Changelog

All notable changes to this repository will be documented in this file.

## [1.0.9] - 2026-01-27

### Fixed
- MongoDB connection error (ECONNREFUSED ::1:27017) by using explicit IPv4 address (127.0.0.1) instead of localhost

### Changed
- Default API port changed from 8080 to 8913 to avoid conflicts with common services

## [1.0.0] - 2026-01-26

### Added
- **xBrowserSync** - Self-hosted bookmark sync service
  - Client-side encryption (password never sent to server)
  - MongoDB database for storing encrypted bookmarks
  - Docker-based deployment
  - Ingress support for Home Assistant sidebar integration
  - Multi-architecture support (amd64, aarch64)

### Removed
- hassio-icloud-backup (migrated to separate repository)
- rdt-client (migrated to separate repository)
- All test and development files

### Changed
- Repository cleaned up and focused on xBrowserSync addon
- Updated repository configuration

## Previous Versions

Earlier versions contained multiple addons that have been split into separate repositories for better maintenance.
