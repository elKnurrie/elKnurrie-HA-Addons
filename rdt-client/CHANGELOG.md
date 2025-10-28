# Changelog

## 0.3.3 (2025-10-28)
### Fixed
- Rewrite Dockerfile to follow Home Assistant add-on standards
- Use proper `ARG BUILD_FROM` and `FROM $BUILD_FROM` pattern
- Replace heredoc syntax with proper run.sh script
- Fix repository URL to point to correct GitHub repository
- Add bashio logging support
- Consolidate package installation with apk

### Changed
- Create dedicated run.sh following Home Assistant conventions
- Improve error handling and logging
- Validate download path configuration

## 0.2.1 (2025-09-02)
- Update repository URLs and docs; automatic download path retained.

## 0.2.0 (2025-09-02)
- Add automatic download path handling using add-on option `download_path`.
- Container startup links `/data/downloads` to the configured path.

## 0.1.2 (2025-09-02)
- Exposed `download_path` as GUI option.

## 0.1.0 (2025-09-02)
- Initial release of the Home Assistant add-on for rdt-client.
