# Home Assistant iCloud Backup# Home Assistant iCloud Backup# Home Assistant iCloud Backup# Home Assistant iCloud Backup Add-on



Automatically backup your Home Assistant snapshots to iCloud Drive using rclone.



## ⚠️ Important: Why 2FA is RequiredAutomatically backup your Home Assistant snapshots to iCloud Drive using rclone.



**Even with app-specific passwords, iCloud Drive requires a ONE-TIME 2FA handshake.**



This is an Apple/iCloud limitation, not an add-on issue:## 🚀 Quick StartAutomatically backup your Home Assistant snapshots to iCloud Drive using rclone.⚠️ **IMPORTANT: Current Status** ⚠️

- ✅ App-specific passwords bypass 2FA for **authentication**  

- ❌ But iCloud Drive API requires **trust tokens**

- 🔑 Trust tokens can ONLY be obtained through **2FA handshake**

- 💾 After initial setup, tokens are saved permanently### 1. Configure the Add-on

- 🎉 **You only do 2FA ONCE - then never again!**



This is unavoidable - it's how Apple's iCloud Drive API works.

- **icloud_username**: Your Apple ID email## 🚀 Quick StartThis add-on uses rclone's iCloud Drive backend, which **requires interactive terminal authentication**. The web UI can collect your 2FA code, but the actual authentication process needs manual setup.

## 🚀 Quick Start

- **icloud_password**: Your Apple ID password (or app-specific password)

### 1. Generate App-Specific Password

- **backup_source**: `/backup` (default)

**You MUST use an app-specific password (not your regular Apple ID password):**

- **icloud_folder**: Folder name in iCloud Drive (default: `HomeAssistantBackups`)

1. Go to https://appleid.apple.com/account/manage

2. Sign in with your Apple ID- **retention_days**: How many days to keep backups (default: 14)### 1. Configure the Add-on## Known Limitation

3. Under "Security" → "App-Specific Passwords" → Generate

4. Label it "Home Assistant" and copy the password



### 2. Configure the Add-on### 2. Start the Add-on



- **icloud_username**: Your Apple ID email

- **icloud_password**: The app-specific password you just created

- **backup_source**: `/backup` (default)The add-on will detect it needs 2FA authentication and show instructions in the logs.- **icloud_username**: Your Apple ID emailRclone's iCloud Drive backend requires:

- **icloud_folder**: Folder name in iCloud Drive (default: `HomeAssistantBackups`)

- **retention_days**: How many days to keep backups (default: 14)



### 3. Start the Add-on### 3. Authenticate (One-Time Setup)- **icloud_password**: Your Apple ID password (or app-specific password)1. Interactive terminal access for first-time authentication



The add-on will detect it needs trust tokens and show instructions in the logs.



### 4. Perform ONE-TIME 2FA SetupOpen **Home Assistant Terminal** (Settings → System → Terminal).- **backup_source**: `/backup` (default)2. Manual entry of 2FA code during the rclone config process



Open **Home Assistant Terminal** (Settings → System → Terminal).



**Step A: Find your Home Assistant IP address****Step A: Find your Home Assistant IP address**- **icloud_folder**: Folder name in iCloud Drive (default: `HomeAssistantBackups`)3. Session tokens are then saved for future use

```bash

hostname -I | awk '{print $1}'```bash

```

Note the IP address (e.g., `192.168.1.100`)hostname -I | awk '{print $1}'- **retention_days**: How many days to keep backups (default: 14)



**Step B: Request trust token** (replace `YOUR_HA_IP` with your actual IP)```

```bash

curl http://YOUR_HA_IP:8099/request_code -X POSTNote the IP address (e.g., `192.168.1.100`)**This cannot be fully automated through a web interface** due to how rclone's authentication works.

```



**Expected response:**

```json**Step B: Request 2FA code** (replace `YOUR_HA_IP` with your actual IP)### 2. Start the Add-on

{

  "success": true,```bash

  "message": "Apple should send a 2FA code to your devices now...",

  "note": "This is a ONE-TIME setup to establish trust tokens..."curl http://YOUR_HA_IP:8099/request_code -X POST## Alternative: Manual Setup via SSH/Terminal

}

``````



**Step C: Check your iPhone/iPad** for the 6-digit codeThe add-on will detect it needs 2FA authentication and show instructions in the logs.



**Step D: Submit the code** (replace both `YOUR_HA_IP` and `123456`)**Expected response:**

```bash

curl http://YOUR_HA_IP:8099/submit_code -X POST -d "123456"```jsonIf you have SSH access to your Home Assistant instance:

```

{

**Expected response:**

```json  "success": true,### 3. Authenticate (One-Time Setup)

{

  "success": true,  "message": "Apple should send a 2FA code to your devices now"

  "message": "Successfully authenticated as your@email.com"

}}```bash

```

```

### 5. Restart the Add-on

Open **Home Assistant Terminal** (Settings → System → Terminal) and run:# Access the add-on container

After successful authentication, restart the add-on. It will now automatically backup your snapshots to iCloud Drive!

**Step C: Check your iPhone/iPad** for the 6-digit code

**You won't need to do 2FA again** - the trust tokens are saved permanently.

docker exec -it addon_local_hassio-icloud-backup /bin/bash

## 📋 How It Works

**Step D: Submit the code** (replace both `YOUR_HA_IP` and `123456`)

1. **First run**: Add-on starts API server for trust token setup

2. **You perform 2FA ONCE** via curl commands in HA Terminal  ```bash```bash

3. **Trust tokens saved**: rclone saves tokens permanently

4. **Automatic backups**: Add-on checks for new snapshots every hour and uploads themcurl http://YOUR_HA_IP:8099/submit_code -X POST -d "123456"

5. **No more 2FA**: Trust tokens persist across restarts

```# Step 1: Request 2FA code# Run rclone config

## 🔧 Troubleshooting



### Port 8099 Not Accessible?

**Expected response:**curl http://localhost:8099/request_code -X POSTrclone config

The add-on exposes port 8099 on your Home Assistant host. Make sure:

- The add-on is running```json

- You're using the correct IP address (run `hostname -I` in HA Terminal)

- Port 8099 isn't blocked by firewall{```



### Check Status  "success": true,

```bash

curl http://YOUR_HA_IP:8099/status  "message": "Successfully authenticated as your@email.com",# Follow the prompts:

```

  "next_step": "Restart the add-on to start backups"

### Get Help

```bash}**Expected response:**# - Choose: n (new remote)

curl http://YOUR_HA_IP:8099/help

``````



### Common Issues```json# - Name: icloud



**"Invalid Session Token" error:**### 4. Restart the Add-on

- This is expected - it means rclone is trying to get trust tokens

- Follow the 2FA setup steps to complete authentication{# - Type: iclouddrive  



**"Connection refused":**After successful authentication, restart the add-on. It will now automatically backup your snapshots to iCloud Drive!

- Make sure you replaced `YOUR_HA_IP` with your actual Home Assistant IP

- Check that port 8099 is listed in the add-on's Configuration → Network  "success": true,# - Enter your Apple ID



**"Invalid code" error:**## 📋 How It Works

- Codes expire in ~60 seconds - request a new one

- Ensure you typed all 6 digits correctly  "message": "Apple should send a 2FA code to your devices now"# - Enter your password

- Try the process again from Step B

1. **First run**: Add-on starts an API server for 2FA authentication

**Need to re-authenticate:**

- If you change your app-specific password2. **You authenticate** via curl commands from HA Terminal  }# - Enter 2FA code when prompted

- Stop the add-on

- Delete `/data/icloud_session_configured` (via File Editor or SSH)3. **Session saved**: rclone saves authentication tokens

- Start add-on and follow 2FA steps again

4. **Automatic backups**: Add-on checks for new snapshots every hour and uploads them```# - Save and exit

### Understanding "Trust Tokens"



When you see errors like "missing icloud trust token":

- This is Apple's security requirement## 🔧 Troubleshooting

- Trust tokens prove your device is authorized

- They're obtained through the initial 2FA handshake

- Once obtained, they're saved and reused automatically

- You won't see this error after successful setup### Port 8099 Not Accessible?**Check your iPhone/iPad** for the 6-digit code.# Exit container



## 🔐 Security Notes



- Use app-specific password (required for iCloud Drive API)The add-on exposes port 8099 on your Home Assistant host. Make sure:exit

- Credentials stored securely in Home Assistant's add-on configuration

- Trust tokens saved in add-on's data directory- The add-on is running

- API only listens on configured port (not exposed to internet)

- Port 8099 only used during initial setup- You're using the correct IP address (run `hostname -I` in HA Terminal)```bash```



## ⚙️ Advanced Configuration- Port 8099 isn't blocked by firewall



### Backup Schedule# Step 2: Submit your code (replace 123456)



The add-on checks for new backups every hour. To change this, modify the `run.sh` script.### Check Status



### iCloud Folder Structure```bashcurl http://localhost:8099/submit_code -X POST -d "123456"After manual setup, the add-on will use the saved session for backups.



Backups are uploaded to: `iCloud Drive/[icloud_folder]/[backup_filename].tar`curl http://YOUR_HA_IP:8099/status



### Retention Policy``````



Backups older than `retention_days` are automatically deleted from iCloud Drive during each sync.



## 📝 Why This Approach?### Get Help## Why This Is Difficult



### Why App-Specific Password?```bash

- Required by Apple for third-party app access

- More secure than using your main passwordcurl http://YOUR_HA_IP:8099/help**Expected response:**

- Can be revoked independently if needed

```

### Why 2FA Despite App-Specific Password?

- App-specific password = bypasses 2FA for authentication ✅```jsonApple's iCloud Drive doesn't have a simple API. Rclone works by:

- But iCloud Drive API = requires trust tokens ❌  

- Trust tokens = obtained only through 2FA handshake 🔑### Common Issues

- This is an Apple/iCloud limitation, not rclone or add-on issue

{1. Starting an interactive authentication session

### Why Terminal/API Instead of Web UI?

- Previous versions had web interface but proved unreliable**"Connection refused" or "Could not resolve host":**

- Ingress routing issues, Flask stability problems

- Terminal + REST API is simpler, more reliable, easier to debug- Make sure you replaced `YOUR_HA_IP` with your actual Home Assistant IP  "success": true,2. Apple sends a 2FA code to your devices  



## 🤝 Support- Try using `127.0.0.1` if running commands directly on the HA host



- **Report issues**: [GitHub Issues](https://github.com/elKnurrie/elKnurrie-HA-Addons/issues)- Check that port 8099 is listed in the add-on's Ports tab  "message": "Successfully authenticated as your@email.com",3. You enter the code in the terminal

- **Check logs**: In the add-on for detailed information

- **API help**: `curl http://YOUR_HA_IP:8099/help`



## 📜 License**"Invalid code" error:**  "next_step": "Restart the add-on to start backups"4. Rclone receives and saves session tokens



MIT License - see repository for details- Codes expire in ~60 seconds - request a new one


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
