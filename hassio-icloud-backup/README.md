# Home Assistant iCloud Backup Add-on

This add-on allows you to automatically upload Home Assistant snapshots/backups to **iCloud Drive** using the official iCloud API via the `pyicloud` Python library.

## ⚠️ Important Note

This add-on uses the **PyiCloud** library which currently does **not support interactive 2FA** (two-factor authentication). You have two options:

1. **Use an app-specific password** (recommended - doesn't require 2FA prompt)
2. **Pre-authenticate and save session** (advanced - requires manual setup)

## Configuration Options

- `icloud_username`: Your Apple ID email address
- `icloud_password`: App-specific password generated from appleid.apple.com
- `backup_source`: Source folder where Home Assistant stores backups (default: `/backup`)
- `icloud_folder`: Folder name in iCloud Drive to store backups (default: `HomeAssistantBackups`)
- `retention_days`: Number of days to keep backups on iCloud before deletion (default: 14, set to 0 to disable)

## Setup Instructions

### Step 1: Create an App-Specific Password

1. Go to https://appleid.apple.com
2. Sign in with your Apple ID
3. Navigate to **Security** section
4. Under **App-Specific Passwords**, click **Generate Password**
5. Enter a label like "Home Assistant Backup"
6. Copy the generated password (format: `xxxx-xxxx-xxxx-xxxx`)

### Step 2: Configure the Add-on

1. Install this add-on from your custom repository
2. Go to the **Configuration** tab
3. Enter your Apple ID email as `icloud_username`
4. Enter the app-specific password as `icloud_password`
5. Adjust other settings as needed
6. Click **Save**

### Step 3: Start the Add-on

1. Go to the **Info** tab
2. Click **Start**
3. Check the **Log** tab to verify it's working

## How It Works

- The add-on connects to iCloud Drive using your Apple ID credentials
- It creates a folder called `HomeAssistantBackups` (or your custom name) in iCloud Drive
- All `.tar` backup files from `/backup` are uploaded to this folder
- Backups older than `retention_days` are automatically deleted from iCloud

## Troubleshooting

### "Two-factor authentication is required!"

The pyicloud library doesn't support interactive 2FA prompts. Make sure you're using an **app-specific password**, not your regular Apple ID password.

### "Failed to login to iCloud"

- Verify your Apple ID email is correct
- Make sure you're using an app-specific password (not your regular password)
- Check that iCloud Drive is enabled in your iCloud settings
- Verify you have enough iCloud storage space

### No backups uploaded

- Make sure backups exist in `/backup` directory
- Check the add-on logs for error messages
- Verify your iCloud credentials are correct

## Notes

- This add-on uploads backups **once when started**
- To run periodic uploads, restart the add-on on a schedule (use Home Assistant automations)
- Large backups may take time to upload depending on your internet speed
- The add-on uses the official iCloud Drive API (not WebDAV)