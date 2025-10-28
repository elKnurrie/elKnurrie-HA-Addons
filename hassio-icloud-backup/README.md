# Home Assistant iCloud Backup Add-on

⚠️ **IMPORTANT: Current Status** ⚠️

This add-on uses rclone's iCloud Drive backend, which **requires interactive terminal authentication**. The web UI can collect your 2FA code, but the actual authentication process needs manual setup.

## Known Limitation

Rclone's iCloud Drive backend requires:
1. Interactive terminal access for first-time authentication
2. Manual entry of 2FA code during the rclone config process
3. Session tokens are then saved for future use

**This cannot be fully automated through a web interface** due to how rclone's authentication works.

## Alternative: Manual Setup via SSH/Terminal

If you have SSH access to your Home Assistant instance:

```bash
# Access the add-on container
docker exec -it addon_local_hassio-icloud-backup /bin/bash

# Run rclone config
rclone config

# Follow the prompts:
# - Choose: n (new remote)
# - Name: icloud
# - Type: iclouddrive  
# - Enter your Apple ID
# - Enter your password
# - Enter 2FA code when prompted
# - Save and exit

# Exit container
exit
```

After manual setup, the add-on will use the saved session for backups.

## Why This Is Difficult

Apple's iCloud Drive doesn't have a simple API. Rclone works by:
1. Starting an interactive authentication session
2. Apple sends a 2FA code to your devices  
3. You enter the code in the terminal
4. Rclone receives and saves session tokens

**We cannot trigger step 2 (Apple sending the code) without interactive terminal access.**

## Recommended Solution

**Use the SSH add-on** to access your Home Assistant terminal and run `rclone config` manually once. After that, this add-on will work automatically for all future backups.

### Easy Setup with Terminal & SSH Add-on:

1. Install "Terminal & SSH" add-on from the official add-on store
2. Start it and open its Web UI
3. Run these commands:
```bash
# Access this add-on's container
docker exec -it addon_local_hassio-icloud-backup /bin/bash

# Run rclone setup
rclone config

# Follow prompts (choose 'n' for new, type 'iclouddrive')
# Enter your Apple ID and password when asked
# Apple will NOW send 2FA code to your iPhone
# Enter the 6-digit code
# Press 'q' to quit config
# Type 'exit' to leave container
```
4. Restart this add-on
5. Done! Backups will now sync automatically

## Configuration Options

## Configuration Options

- `icloud_username`: Your Apple ID email address
- `icloud_password`: Your Apple ID password (or app-specific password)
- `backup_source`: Source folder where Home Assistant stores backups (default: `/backup`)
- `icloud_folder`: Folder name in iCloud Drive (default: `HomeAssistantBackups`)
- `retention_days`: Days to keep old backups (default: 14, set to 0 to disable)

## How Backups Work

- Add-on syncs backups **when started/restarted**
- All `.tar` files from `/backup` are uploaded to iCloud Drive
- Backups older than `retention_days` are automatically deleted from iCloud
- Session token is saved and reused (no 2FA needed after initial setup)

## Automating Backups

To run backups on a schedule, create a Home Assistant automation:

```yaml
automation:
  - alias: "iCloud Backup Daily"
    trigger:
      - platform: time
        at: "03:00:00"
    action:
      - service: hassio.addon_restart
        data:
          addon: "local_hassio-icloud-backup"
```

## Troubleshooting

### "Failed to connect to iCloud Drive"

You need to complete the initial 2FA authentication:
1. Open the add-on terminal
2. Run `rclone config`
3. Complete the authentication with 2FA
4. Restart the add-on

### Session Expired

If your session expires after some time:
1. Run `rclone config` again
2. Re-authenticate with 2FA
3. The new session token will be saved

### "No such file or directory"

Make sure `/backup` contains backup files. Home Assistant stores backups there by default.

## Technical Details

- Uses rclone's `iclouddrive` backend
- Session tokens are stored in `/data/rclone-icloud-session.txt`
- Supports both regular passwords and app-specific passwords
- Handles Apple's 2FA properly through rclone's interactive auth

---

**Status:** ✅ WORKING - Thanks to rclone's native iCloud Drive support!