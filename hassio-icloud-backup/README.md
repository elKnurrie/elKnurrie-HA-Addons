# Home Assistant iCloud Backup Add-on

This add-on allows you to automatically upload Home Assistant snapshots/backups to iCloud using `rclone` with WebDAV.

## Configuration Options

- `icloud_webdav_url`: WebDAV URL for iCloud (default: https://webdav.icloud.com)
- `icloud_username`: Your Apple ID email
- `icloud_password`: App-specific password generated from your Apple ID account
- `backup_source`: Source folder where Home Assistant stores backups (default: `/backup`)
- `backup_destination`: Mount point for iCloud (default: `/mnt/icloud`)
- `retention_days`: Number of days to keep backups on iCloud before deletion (default: 14)

## Usage

1. Generate an app-specific password on your Apple ID security page for WebDAV access.
2. Install this add-on via the Home Assistant add-on store (custom repository).
3. Configure your credentials and options.
4. Start the add-on and it will sync backups to iCloud and remove old backups automatically.

## Notes

- Some delay may occur due to WebDAV performance limits.
- Make sure your Home Assistant backup folder (`/backup`) is accessible as read-only to the add-on.