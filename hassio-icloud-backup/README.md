# Home Assistant iCloud Backup Add-on

✅ **NOW WORKING!** Uses rclone's native iCloud Drive support.

This add-on automatically uploads Home Assistant snapshots/backups to **iCloud Drive** using rclone.

## How It Works

Uses [rclone's iCloud Drive backend](https://rclone.org/iclouddrive/) which properly handles Apple's authentication including 2FA.

## First-Time Setup (2FA Authentication)

On first run, you need to authenticate with iCloud and handle 2FA:

### Step 1: Install and Configure

1. Install this add-on
2. Configure your Apple ID and password in the Configuration tab
3. **Start the add-on** (it will fail - this is expected)

### Step 2: Complete 2FA Authentication

1. Go to the add-on page
2. Click on the **"Open Web UI"** or use the Terminal
3. Run: `rclone config`
4. Follow the interactive prompts:
   - Choose: `n` for new remote (if needed)
   - Type: `iclouddrive`
   - Enter your Apple ID
   - Enter your password (regular password OR app-specific password)
   - **Enter the 2FA code** when prompted
5. The session token will be saved automatically
6. Exit the config: `q`

### Step 3: Restart the Add-on

After completing the rclone config, **restart the add-on**. It will now use the saved session token and work without prompting for 2FA again!

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