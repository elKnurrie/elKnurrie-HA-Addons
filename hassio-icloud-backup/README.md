# Home Assistant iCloud Backup# Home Assistant iCloud Backup# Home Assistant iCloud Backup Add-on



Automatically backup your Home Assistant snapshots to iCloud Drive using rclone.



## 🚀 Quick StartAutomatically backup your Home Assistant snapshots to iCloud Drive using rclone.⚠️ **IMPORTANT: Current Status** ⚠️



### 1. Configure the Add-on



- **icloud_username**: Your Apple ID email## 🚀 Quick StartThis add-on uses rclone's iCloud Drive backend, which **requires interactive terminal authentication**. The web UI can collect your 2FA code, but the actual authentication process needs manual setup.

- **icloud_password**: Your Apple ID password (or app-specific password)

- **backup_source**: `/backup` (default)

- **icloud_folder**: Folder name in iCloud Drive (default: `HomeAssistantBackups`)

- **retention_days**: How many days to keep backups (default: 14)### 1. Configure the Add-on## Known Limitation



### 2. Start the Add-on



The add-on will detect it needs 2FA authentication and show instructions in the logs.- **icloud_username**: Your Apple ID emailRclone's iCloud Drive backend requires:



### 3. Authenticate (One-Time Setup)- **icloud_password**: Your Apple ID password (or app-specific password)1. Interactive terminal access for first-time authentication



Open **Home Assistant Terminal** (Settings → System → Terminal).- **backup_source**: `/backup` (default)2. Manual entry of 2FA code during the rclone config process



**Step A: Find your Home Assistant IP address**- **icloud_folder**: Folder name in iCloud Drive (default: `HomeAssistantBackups`)3. Session tokens are then saved for future use

```bash

hostname -I | awk '{print $1}'- **retention_days**: How many days to keep backups (default: 14)

```

Note the IP address (e.g., `192.168.1.100`)**This cannot be fully automated through a web interface** due to how rclone's authentication works.



**Step B: Request 2FA code** (replace `YOUR_HA_IP` with your actual IP)### 2. Start the Add-on

```bash

curl http://YOUR_HA_IP:8099/request_code -X POST## Alternative: Manual Setup via SSH/Terminal

```

The add-on will detect it needs 2FA authentication and show instructions in the logs.

**Expected response:**

```jsonIf you have SSH access to your Home Assistant instance:

{

  "success": true,### 3. Authenticate (One-Time Setup)

  "message": "Apple should send a 2FA code to your devices now"

}```bash

```

Open **Home Assistant Terminal** (Settings → System → Terminal) and run:# Access the add-on container

**Step C: Check your iPhone/iPad** for the 6-digit code

docker exec -it addon_local_hassio-icloud-backup /bin/bash

**Step D: Submit the code** (replace both `YOUR_HA_IP` and `123456`)

```bash```bash

curl http://YOUR_HA_IP:8099/submit_code -X POST -d "123456"

```# Step 1: Request 2FA code# Run rclone config



**Expected response:**curl http://localhost:8099/request_code -X POSTrclone config

```json

{```

  "success": true,

  "message": "Successfully authenticated as your@email.com",# Follow the prompts:

  "next_step": "Restart the add-on to start backups"

}**Expected response:**# - Choose: n (new remote)

```

```json# - Name: icloud

### 4. Restart the Add-on

{# - Type: iclouddrive  

After successful authentication, restart the add-on. It will now automatically backup your snapshots to iCloud Drive!

  "success": true,# - Enter your Apple ID

## 📋 How It Works

  "message": "Apple should send a 2FA code to your devices now"# - Enter your password

1. **First run**: Add-on starts an API server for 2FA authentication

2. **You authenticate** via curl commands from HA Terminal  }# - Enter 2FA code when prompted

3. **Session saved**: rclone saves authentication tokens

4. **Automatic backups**: Add-on checks for new snapshots every hour and uploads them```# - Save and exit



## 🔧 Troubleshooting



### Port 8099 Not Accessible?**Check your iPhone/iPad** for the 6-digit code.# Exit container



The add-on exposes port 8099 on your Home Assistant host. Make sure:exit

- The add-on is running

- You're using the correct IP address (run `hostname -I` in HA Terminal)```bash```

- Port 8099 isn't blocked by firewall

# Step 2: Submit your code (replace 123456)

### Check Status

```bashcurl http://localhost:8099/submit_code -X POST -d "123456"After manual setup, the add-on will use the saved session for backups.

curl http://YOUR_HA_IP:8099/status

``````



### Get Help## Why This Is Difficult

```bash

curl http://YOUR_HA_IP:8099/help**Expected response:**

```

```jsonApple's iCloud Drive doesn't have a simple API. Rclone works by:

### Common Issues

{1. Starting an interactive authentication session

**"Connection refused" or "Could not resolve host":**

- Make sure you replaced `YOUR_HA_IP` with your actual Home Assistant IP  "success": true,2. Apple sends a 2FA code to your devices  

- Try using `127.0.0.1` if running commands directly on the HA host

- Check that port 8099 is listed in the add-on's Ports tab  "message": "Successfully authenticated as your@email.com",3. You enter the code in the terminal



**"Invalid code" error:**  "next_step": "Restart the add-on to start backups"4. Rclone receives and saves session tokens

- Codes expire in ~60 seconds - request a new one

- Ensure you typed all 6 digits correctly}

- Try the process again from Step B

```**We cannot trigger step 2 (Apple sending the code) without interactive terminal access.**

**"No authentication in progress":**

- You need to run `/request_code` first

- Each code request starts a new authentication session

### 4. Restart the Add-on## Recommended Solution

**API not responding:**

- Check add-on logs for errors

- Ensure add-on is running

- Verify the API server started (look for "✅ API server is ready" in logs)After successful authentication, restart the add-on. It will now automatically backup your snapshots to iCloud Drive!**Use the SSH add-on** to access your Home Assistant terminal and run `rclone config` manually once. After that, this add-on will work automatically for all future backups.



### Re-authenticate



If you need to re-authenticate (e.g., password changed):## 📋 How It Works### Easy Setup with Terminal & SSH Add-on:



1. Stop the add-on

2. Delete `/data/icloud_session_configured` (via File Editor add-on or SSH)

3. Start the add-on1. **First run**: Add-on starts an API server for 2FA authentication1. Install "Terminal & SSH" add-on from the official add-on store

4. Follow authentication steps again

2. **You authenticate** via simple curl commands in HA Terminal2. Start it and open its Web UI

## 🔐 Security Notes

3. **Session saved**: rclone saves authentication tokens3. Run these commands:

- Your Apple ID credentials are stored in Home Assistant's add-on configuration (encrypted)

- Authentication tokens are saved in the add-on's data directory4. **Automatic backups**: Add-on checks for new snapshots every hour and uploads them```bash

- The API only listens on the configured port (accessible within your network)

- No data leaves your network except the connection to iCloud# Access this add-on's container

- Port 8099 is only used during initial authentication

## 🔧 Troubleshootingdocker exec -it addon_local_hassio-icloud-backup /bin/bash

## ⚙️ Advanced Configuration



### Backup Schedule

### Check Status# Run rclone setup

The add-on checks for new backups every hour. To change this, modify the `run.sh` script.

```bashrclone config

### iCloud Folder Structure

curl http://localhost:8099/status

Backups are uploaded to: `iCloud Drive/[icloud_folder]/[backup_filename].tar`

```# Follow prompts (choose 'n' for new, type 'iclouddrive')

### Retention Policy

# Enter your Apple ID and password when asked

Backups older than `retention_days` are automatically deleted from iCloud Drive during each sync.

### Get Help# Apple will NOW send 2FA code to your iPhone

## 📝 Why Terminal/API Instead of Web UI?

```bash# Enter the 6-digit code

Previous versions had a web interface, but it proved unreliable in the Home Assistant environment due to:

- Ingress routing issues  curl http://localhost:8099/help# Press 'q' to quit config

- Flask/HTTP server stability problems

- Complex troubleshooting across different HA configurations```# Type 'exit' to leave container



The current approach using Terminal + REST API is:```

- ✅ **Simpler** - just curl commands

- ✅ **More reliable** - no browser/Ingress routing issues### Common Issues4. Restart this add-on

- ✅ **Easier to debug** - clear JSON responses

- ✅ **Works everywhere** - direct HTTP calls to exposed port5. Done! Backups will now sync automatically

- ✅ **Transparent** - you see exactly what's happening

**"Invalid code" error:**

## 💡 Alternative: Use from Any Computer

- Codes expire in ~60 seconds - request a new one## Configuration Options

Since port 8099 is exposed, you can also run the curl commands from any computer on your network:

- Ensure you typed all 6 digits correctly

```bash

# From your laptop/desktop (replace YOUR_HA_IP)- Try the process again from Step 1## Configuration Options

curl http://YOUR_HA_IP:8099/request_code -X POST

curl http://YOUR_HA_IP:8099/submit_code -X POST -d "123456"

```

**"No authentication in progress":**- `icloud_username`: Your Apple ID email address

## 🤝 Support

- You need to run `/request_code` first- `icloud_password`: Your Apple ID password (or app-specific password)

- **Report issues**: [GitHub Issues](https://github.com/elKnurrie/elKnurrie-HA-Addons/issues)

- **Check logs**: In the add-on for detailed information- Each code request starts a new authentication session- `backup_source`: Source folder where Home Assistant stores backups (default: `/backup`)

- **API help**: `curl http://YOUR_HA_IP:8099/help`

- `icloud_folder`: Folder name in iCloud Drive (default: `HomeAssistantBackups`)

## 📜 License

**API not responding:**- `retention_days`: Days to keep old backups (default: 14, set to 0 to disable)

MIT License - see repository for details

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
