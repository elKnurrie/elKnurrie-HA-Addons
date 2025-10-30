# Home Assistant iCloud Backup# Home Assistant iCloud Backup Add-on



Automatically backup your Home Assistant snapshots to iCloud Drive using rclone.⚠️ **IMPORTANT: Current Status** ⚠️



## 🚀 Quick StartThis add-on uses rclone's iCloud Drive backend, which **requires interactive terminal authentication**. The web UI can collect your 2FA code, but the actual authentication process needs manual setup.



### 1. Configure the Add-on## Known Limitation



- **icloud_username**: Your Apple ID emailRclone's iCloud Drive backend requires:

- **icloud_password**: Your Apple ID password (or app-specific password)1. Interactive terminal access for first-time authentication

- **backup_source**: `/backup` (default)2. Manual entry of 2FA code during the rclone config process

- **icloud_folder**: Folder name in iCloud Drive (default: `HomeAssistantBackups`)3. Session tokens are then saved for future use

- **retention_days**: How many days to keep backups (default: 14)

**This cannot be fully automated through a web interface** due to how rclone's authentication works.

### 2. Start the Add-on

## Alternative: Manual Setup via SSH/Terminal

The add-on will detect it needs 2FA authentication and show instructions in the logs.

If you have SSH access to your Home Assistant instance:

### 3. Authenticate (One-Time Setup)

```bash

Open **Home Assistant Terminal** (Settings → System → Terminal) and run:# Access the add-on container

docker exec -it addon_local_hassio-icloud-backup /bin/bash

```bash

# Step 1: Request 2FA code# Run rclone config

curl http://localhost:8099/request_code -X POSTrclone config

```

# Follow the prompts:

**Expected response:**# - Choose: n (new remote)

```json# - Name: icloud

{# - Type: iclouddrive  

  "success": true,# - Enter your Apple ID

  "message": "Apple should send a 2FA code to your devices now"# - Enter your password

}# - Enter 2FA code when prompted

```# - Save and exit



**Check your iPhone/iPad** for the 6-digit code.# Exit container

exit

```bash```

# Step 2: Submit your code (replace 123456)

curl http://localhost:8099/submit_code -X POST -d "123456"After manual setup, the add-on will use the saved session for backups.

```

## Why This Is Difficult

**Expected response:**

```jsonApple's iCloud Drive doesn't have a simple API. Rclone works by:

{1. Starting an interactive authentication session

  "success": true,2. Apple sends a 2FA code to your devices  

  "message": "Successfully authenticated as your@email.com",3. You enter the code in the terminal

  "next_step": "Restart the add-on to start backups"4. Rclone receives and saves session tokens

}

```**We cannot trigger step 2 (Apple sending the code) without interactive terminal access.**



### 4. Restart the Add-on## Recommended Solution



After successful authentication, restart the add-on. It will now automatically backup your snapshots to iCloud Drive!**Use the SSH add-on** to access your Home Assistant terminal and run `rclone config` manually once. After that, this add-on will work automatically for all future backups.



## 📋 How It Works### Easy Setup with Terminal & SSH Add-on:



1. **First run**: Add-on starts an API server for 2FA authentication1. Install "Terminal & SSH" add-on from the official add-on store

2. **You authenticate** via simple curl commands in HA Terminal2. Start it and open its Web UI

3. **Session saved**: rclone saves authentication tokens3. Run these commands:

4. **Automatic backups**: Add-on checks for new snapshots every hour and uploads them```bash

# Access this add-on's container

## 🔧 Troubleshootingdocker exec -it addon_local_hassio-icloud-backup /bin/bash



### Check Status# Run rclone setup

```bashrclone config

curl http://localhost:8099/status

```# Follow prompts (choose 'n' for new, type 'iclouddrive')

# Enter your Apple ID and password when asked

### Get Help# Apple will NOW send 2FA code to your iPhone

```bash# Enter the 6-digit code

curl http://localhost:8099/help# Press 'q' to quit config

```# Type 'exit' to leave container

```

### Common Issues4. Restart this add-on

5. Done! Backups will now sync automatically

**"Invalid code" error:**

- Codes expire in ~60 seconds - request a new one## Configuration Options

- Ensure you typed all 6 digits correctly

- Try the process again from Step 1## Configuration Options



**"No authentication in progress":**- `icloud_username`: Your Apple ID email address

- You need to run `/request_code` first- `icloud_password`: Your Apple ID password (or app-specific password)

- Each code request starts a new authentication session- `backup_source`: Source folder where Home Assistant stores backups (default: `/backup`)

- `icloud_folder`: Folder name in iCloud Drive (default: `HomeAssistantBackups`)

**API not responding:**- `retention_days`: Days to keep old backups (default: 14, set to 0 to disable)

- Check add-on logs

- Ensure add-on is running## How Backups Work

- The API runs on localhost:8099

- Add-on syncs backups **when started/restarted**

### Re-authenticate- All `.tar` files from `/backup` are uploaded to iCloud Drive

- Backups older than `retention_days` are automatically deleted from iCloud

If you need to re-authenticate (e.g., password changed):- Session token is saved and reused (no 2FA needed after initial setup)



1. Stop the add-on## Automating Backups

2. Delete `/data/icloud_session_configured` (via File Editor or SSH)

3. Start the add-onTo run backups on a schedule, create a Home Assistant automation:

4. Follow authentication steps again

```yaml

## 🔐 Security Notesautomation:

  - alias: "iCloud Backup Daily"

- Your Apple ID credentials are stored in Home Assistant's add-on configuration    trigger:

- Authentication tokens are saved in the add-on's data directory      - platform: time

- The API only listens on localhost (not exposed to network)        at: "03:00:00"

- No data leaves your network except the connection to iCloud    action:

      - service: hassio.addon_restart

## ⚙️ Advanced Configuration        data:

          addon: "local_hassio-icloud-backup"

### Backup Schedule```



The add-on checks for new backups every hour. To change this, you'll need to modify the `run.sh` script.## Troubleshooting



### iCloud Folder Structure### "Failed to connect to iCloud Drive"



Backups are uploaded to: `iCloud Drive/[icloud_folder]/[backup_filename].tar`You need to complete the initial 2FA authentication:

1. Open the add-on terminal

### Retention Policy2. Run `rclone config`

3. Complete the authentication with 2FA

Backups older than `retention_days` are automatically deleted from iCloud Drive during each sync.4. Restart the add-on



## 📝 Why Terminal/API Instead of Web UI?### Session Expired



Previous versions had a web interface, but it proved unreliable in the Home Assistant environment due to:If your session expires after some time:

- Ingress routing issues1. Run `rclone config` again

- Flask/HTTP server stability problems  2. Re-authenticate with 2FA

- Complex troubleshooting3. The new session token will be saved



The current approach using Terminal + REST API is:### "No such file or directory"

- ✅ **Simpler** - just curl commands

- ✅ **More reliable** - no browser/routing issuesMake sure `/backup` contains backup files. Home Assistant stores backups there by default.

- ✅ **Easier to debug** - clear JSON responses

- ✅ **Works every time** - direct HTTP calls## Technical Details



## 🤝 Support- Uses rclone's `iclouddrive` backend

- Session tokens are stored in `/data/rclone-icloud-session.txt`

- Report issues: [GitHub Issues](https://github.com/elKnurrie/elKnurrie-HA-Addons/issues)- Supports both regular passwords and app-specific passwords

- Check logs in the add-on for detailed information- Handles Apple's 2FA properly through rclone's interactive auth

- Use `/help` endpoint for quick reference

---

## 📜 License

**Status:** ✅ WORKING - Thanks to rclone's native iCloud Drive support!
MIT License - see repository for details
