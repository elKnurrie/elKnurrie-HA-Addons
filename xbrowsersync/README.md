# xBrowserSync Addon for Home Assistant

Self-hosted bookmark sync service with client-side encryption. Sync your browser bookmarks across devices without sending your data to third-party servers.

## Features

- Client-side encryption (your password is never sent to the server)
- No registration required - just sync ID and password
- Self-hosted for complete privacy
- Works with Chrome, Firefox, and mobile apps

## Installation

1. Add this repository to Home Assistant:
   - Go to **Settings** → **Add-ons** → **Add-on store**
   - Click the **three dots** → **Repositories**
   - Add: `https://github.com/elKnurrie/elKnurrie-HA-Addons`

2. Install the **xBrowserSync** addon

3. Configure the addon:
   - Set a strong `db_password`
   - Optionally change the `api_port`

4. Start the addon

## Configuration

### Addon Options

| Option | Description | Default |
|--------|-------------|---------|
| `db_password` | Database password (required) | - |
| `api_port` | Port for the API | 8913 |

### Ingress Setup (Optional)

To add xBrowserSync to your Home Assistant sidebar using Ingress:

1. Install [HACS](https://hacs.xyz/) if not already installed

2. Install the **Ingress** integration from HACS:
   - HACS → Frontend → Search "Ingress"

3. Add to your `configuration.yaml`:

```yaml
ingress:
  xbrowsersync:
    work_mode: side-panel
    ui_mode: toolbar
    title: "Bookmarks"
    icon: mdi:bookmark
    url: http://localhost:8913
```

4. Restart Home Assistant

## Usage

### Get Your Server URL

The addon runs internally. Use:
- **Internal:** `http://localhost:8913` (from Home Assistant host)
- **External:** Your Home Assistant external URL (if using Ingress)

### Browser Extension Setup

1. Install xBrowserSync extension for [Chrome](https://chrome.google.com/webstore/detail/xbrowsersync/lcjblhmjhmnhgomiijdnemidfocfekpf) or [Firefox](https://addons.mozilla.org/firefox/addon/xbrowsersync/)

2. Click the extension icon → **Settings**

3. Enter your server URL:
   - For Ingress: `https://your-ha-domain.com/api/hubs/xbrowsersync`
   - Direct: `http://your-ha-ip:8913`

4. Create a new sync with a strong encryption password

### Mobile Apps

- iOS: Search "xBrowserSync" in App Store
- Android: Search "xBrowserSync" in Play Store

## Troubleshooting

### Can't connect from browser extension

- Ensure the addon is running
- Check if the port is accessible from your network
- For Ingress, make sure the URL matches your HA configuration

### MongoDB issues

- Check addon logs for MongoDB errors
- Try removing and reinstalling the addon to reset the database

## Support

- [xBrowserSync Official](https://www.xbrowsersync.org/)
- [xBrowserSync GitHub](https://github.com/xbrowsersync)
