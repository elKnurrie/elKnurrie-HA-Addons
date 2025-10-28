# RDT Client (Home Assistant Add-on)

**Version 0.3.2**

This add-on runs the official `rogerfar/rdtclient` container, providing Real-Debrid torrent client functionality within Home Assistant.

## Configuration

Set the **download_path** from the add-on UI (default: `/share/rdt-downloads`).

The add-on will automatically create the download folder if it doesn't exist and make it available to RDT Client.

**Note:** You may need to manually configure the download path within RDT Client's settings after first startup.

### First-run steps

1. Start the add-on and open the Web UI
2. In RDT Client settings, configure your download path to match the path you set in the add-on configuration
3. Keep the default **Database path** `/data/db/rdtclient.db`

## Ports
- **6500/tcp** – Web UI

## Data locations (inside the container)
- `/data/db` – SQLite database (`rdtclient.db`)
- `/share/rdt-downloads` – Default download path (or your configured path)

## Troubleshooting
- If the add-on doesn't appear, click **Add-on Store → ⋮ → Reload**.
- Ensure your configured path lives under `/share` and is writable.
- If you encounter build issues, make sure you're using the latest version of the add-on.
- **Note**: You may need to manually set the download path in RDT Client's settings after first startup.

## Recent Updates (v0.3.2)
- **Enhanced S6 overlay permissions**: Fixed s6-mkdir permission denied errors for /run/s6 and /run/service
- **Comprehensive AppArmor capabilities**: Added all necessary capabilities for S6 overlay operations
- **Better runtime directory support**: Enhanced permissions for /run, /var, /proc, and /sys directories
- **Improved S6 binary access**: Complete permission coverage for all S6 overlay binaries and tools

### Previous Updates (v0.3.1)
- **Fixed init system compatibility**: Custom init wrapper that works with the base image's existing init system
- **Preserved original functionality**: Delegates to the original `/init` after running Home Assistant setup
- **Enhanced AppArmor support**: Added permissions for both custom scripts and original S6 overlay system
- **Better integration**: Works with the base image's existing architecture instead of replacing it

### Previous Updates (v0.3.0)
- **Major Simplification**: Removed S6 overlay dependencies that were causing permission issues
- **Simplified startup process**: Custom startup script instead of complex S6 overlay system  
- **Cleaner AppArmor profile**: Minimal, focused security profile without unnecessary complexity
- **Manual configuration**: Removed automatic symlink setup - users configure download path in RDT Client directly
- **Better reliability**: No more init system conflicts or permission denied errors

### Previous Updates (v0.2.x)
- Multiple attempts to fix S6 overlay permission issues (v0.2.2 through v0.2.7)
- Fixed Docker build issues with Alpine Linux package manager
- Enhanced AppArmor profiles for better compatibility

### Previous Updates (v0.2.4)
- **Fixed init script permissions**: Resolved "/init: Permission denied" error during container startup
- **Enhanced AppArmor capabilities**: Added necessary permissions for chown, setuid, setgid operations
- **Improved container initialization**: Added explicit permission setting for init scripts

### Previous Updates (v0.2.3)
- **Fixed AppArmor profile issues**: Resolved installation errors related to security profile loading
- **Enhanced security permissions**: Updated AppArmor configuration for better Home Assistant compatibility
- **Improved network and file system access**: Added support for IPv6 and additional system paths

### Previous Updates (v0.2.2)
- Fixed Docker build issues by updating package manager commands for Alpine Linux compatibility
- Improved error handling and setup process
