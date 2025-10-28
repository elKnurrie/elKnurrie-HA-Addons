# Home Assistant iCloud Backup Add-on

⚠️ **PROJECT STATUS: ON HOLD** ⚠️

This add-on is currently **non-functional** due to Apple's iCloud Drive API limitations.

## Issue

Apple's iCloud Drive does not support authentication via app-specific passwords through the pyicloud API. The add-on successfully receives credentials but Apple's API rejects all authentication attempts.

## What Was Tried

1. ✅ WebDAV approach - Failed (webdav.icloud.com doesn't exist)
2. ✅ PyiCloud library - Failed (doesn't support app-specific passwords for Drive)
3. ✅ PyiCloud-ipd fork - Failed (same authentication limitation)
4. ✅ Various authentication methods - All failed

## Root Cause

Apple intentionally restricts iCloud Drive API access to prevent third-party applications from accessing files programmatically. App-specific passwords work for Mail, Calendar, and Contacts (CalDAV/CardDAV), but NOT for iCloud Drive.

## Alternative Solutions

### 1. Use Google Drive Instead
- Reliable, well-supported
- Works perfectly with rclone
- Free 15GB storage
- **Recommended alternative**

### 2. Use Dropbox or OneDrive
- Both have excellent API support
- Work well with Home Assistant add-ons

### 3. Mac Bridge Setup
- Mount iCloud Drive on a Mac
- Use Home Assistant to sync to Mac via SMB/SFTP
- Mac automatically syncs to iCloud Drive

### 4. Local NAS/Network Storage
- More control
- No cloud storage limits
- Faster transfers

## Configuration (Non-functional)

The add-on is configured but will not work until Apple provides proper API access.

- `icloud_username`: Your Apple ID email address
- `icloud_password`: App-specific password (doesn't work for Drive access)
- `backup_source`: `/backup`
- `icloud_folder`: `HomeAssistantBackups`
- `retention_days`: 14

## For Developers

If you find a way to make this work, please contribute! The codebase is ready - only authentication is blocked by Apple.

---

**Last Updated:** October 28, 2025  
**Status:** Suspended indefinitely