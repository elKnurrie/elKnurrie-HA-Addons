#!/usr/bin/with-contenv bashio

set -e

CONFIG_FILE=/data/options.json

ICLOUD_USERNAME=$(jq --raw-output '.icloud_username' "$CONFIG_FILE")
ICLOUD_PASSWORD=$(jq --raw-output '.icloud_password' "$CONFIG_FILE")
BACKUP_SOURCE=$(jq --raw-output '.backup_source' "$CONFIG_FILE")
ICLOUD_FOLDER=$(jq --raw-output '.icloud_folder' "$CONFIG_FILE")
RETENTION_DAYS=$(jq --raw-output '.retention_days' "$CONFIG_FILE")

bashio::log.info "Starting iCloud Backup add-on..."

# Validate required configuration
if [ -z "$ICLOUD_USERNAME" ] || [ -z "$ICLOUD_PASSWORD" ]; then
    bashio::log.error "iCloud username and password are required!"
    exit 1
fi

# Create rclone config directory
mkdir -p /root/.config/rclone

# Check if we have a saved session or need to do initial setup
if [ ! -f /data/icloud_session_configured ]; then
    bashio::log.warning "⚠️  First-time setup required!"
    bashio::log.info ""
    bashio::log.info "Please follow these steps:"
    bashio::log.info "  1. Click 'OPEN WEB UI' button in the add-on page"
    bashio::log.info "  2. Check your iPhone/iPad for the 2FA code"
    bashio::log.info "  3. Enter the 6-digit code in the web form"
    bashio::log.info "  4. Wait for authentication to complete"
    bashio::log.info "  5. Restart this add-on"
    bashio::log.info ""
    
    # Create initial rclone config
    cat > /root/.config/rclone/rclone.conf <<EOF
[icloud]
type = iclouddrive
user = $ICLOUD_USERNAME
pass = $(rclone obscure "$ICLOUD_PASSWORD")
EOF
    
    # Check if 2FA code has been provided
    if [ -f /data/icloud_2fa_code.txt ]; then
        bashio::log.info "2FA code found! Attempting authentication..."
        
        TWOFA_CODE=$(cat /data/icloud_2fa_code.txt)
        bashio::log.info "Using 2FA code: $TWOFA_CODE"
        
        # Try to authenticate with rclone
        # This will trigger the authentication and Apple will send 2FA to devices
        bashio::log.info "Triggering iCloud authentication (this will send 2FA to your devices)..."
        
        if echo "$TWOFA_CODE" | timeout 60 rclone lsd icloud: --verbose 2>&1; then
            bashio::log.info "✅ Authentication successful!"
            touch /data/icloud_session_configured
            rm /data/icloud_2fa_code.txt
            
            bashio::log.info "Session saved! Please restart the add-on to begin backups."
        else
            bashio::log.error "❌ Authentication failed. Please check:"
            bashio::log.error "  - Is the 2FA code correct?"
            bashio::log.error "  - Did you enter it quickly enough? (codes expire)"
            bashio::log.error "  - Are your Apple ID credentials correct?"
            bashio::log.info ""
            bashio::log.info "Delete /data/icloud_2fa_code.txt and try again with a new code"
        fi
    else
        bashio::log.info "Waiting for 2FA authentication..."
    fi
    
    # Start the API server
    bashio::log.info ""
    bashio::log.info "╔══════════════════════════════════════════════════════════╗"
    bashio::log.info "║  iCloud 2FA Setup Required                              ║"
    bashio::log.info "╚══════════════════════════════════════════════════════════╝"
    bashio::log.info ""
    bashio::log.info "The API server is running on port 8099"
    bashio::log.info ""
    bashio::log.info "Open Home Assistant Terminal and run:"
    bashio::log.info ""
    bashio::log.info "# Get your Home Assistant IP (if you don't know it):"
    bashio::log.info "hostname -I | awk '{print \$1}'"
    bashio::log.info ""
    bashio::log.info "# Then use that IP in the commands below:"
    bashio::log.info ""
    bashio::log.info "1️⃣  Request 2FA code:"
    bashio::log.info "   curl http://YOUR_HA_IP:8099/request_code -X POST"
    bashio::log.info ""
    bashio::log.info "2️⃣  Check your iPhone/iPad for the 6-digit code"
    bashio::log.info ""
    bashio::log.info "3️⃣  Submit the code (replace 123456 with your actual code):"
    bashio::log.info "   curl http://YOUR_HA_IP:8099/submit_code -X POST -d \"123456\""
    bashio::log.info ""
    bashio::log.info "4️⃣  Restart this add-on after successful authentication"
    bashio::log.info ""
    bashio::log.info "Starting API server on port 8099..."
    
    python3 -u /auth_api.py &
    
    # Wait for server to start
    sleep 3
    
    # Check if server is running
    if pgrep -f "auth_api.py" > /dev/null 2>&1; then
        bashio::log.info "✅ API server is ready"
        bashio::log.info "💡 Access it from Home Assistant host at port 8099"
    else
        bashio::log.error "❌ API server failed to start"
        exit 1
    fi
    
    # Keep running and wait for authentication
    tail -f /dev/null
fi

bashio::log.info "Using saved iCloud session..."

# Create rclone config with saved tokens
cat > /root/.config/rclone/rclone.conf <<EOF
[icloud]
type = iclouddrive
user = $ICLOUD_USERNAME
pass = $(rclone obscure "$ICLOUD_PASSWORD")
EOF

bashio::log.info "Testing iCloud Drive connection..."

if ! rclone lsd icloud: --verbose 2>&1 | tee /tmp/rclone-debug.log; then
    bashio::log.error "Failed to connect to iCloud Drive."
    bashio::log.error "Session may have expired. Removing saved session..."
    rm -f /data/icloud_session_configured
    bashio::log.info "Please restart the add-on to re-authenticate"
    cat /tmp/rclone-debug.log || true
    exit 1
fi

bashio::log.info "✅ iCloud Drive connection successful!"

# Sync backups
bashio::log.info "Syncing backups from $BACKUP_SOURCE to iCloud Drive..."
rclone sync "$BACKUP_SOURCE" "icloud:$ICLOUD_FOLDER" --create-empty-src-dirs --verbose

# Remove old backups
if [ "$RETENTION_DAYS" -gt 0 ]; then
    bashio::log.info "Removing backups older than $RETENTION_DAYS days..."
    rclone delete --min-age ${RETENTION_DAYS}d "icloud:$ICLOUD_FOLDER" --verbose
fi

bashio::log.info "✅ Backup sync complete!"

# Keep addon running
tail -f /dev/null
