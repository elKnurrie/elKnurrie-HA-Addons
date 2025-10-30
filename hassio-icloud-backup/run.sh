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
        bashio::log.info "Waiting for 2FA code via Web UI..."
    fi
    
    # Start the web setup interface
    bashio::log.info "Starting web interface on port ${INGRESS_PORT:-8099}..."
    python3 /setup_server.py 2>/data/flask_error.log &
    FLASK_PID=$!
    bashio::log.info "Flask PID: $FLASK_PID"
    
    # Wait for Flask to start and bind to port
    sleep 5
    
    # Show any errors from Flask
    if [ -f /data/flask_error.log ] && [ -s /data/flask_error.log ]; then
        bashio::log.warning "Flask stderr output:"
        cat /data/flask_error.log
    fi
    
    # Check if Flask is still running
    if ps -p $FLASK_PID > /dev/null 2>&1; then
        bashio::log.info "✅ Flask server started successfully (PID: $FLASK_PID)"
        
        # Try to connect to Flask to verify it's responding
        if curl -f http://localhost:${INGRESS_PORT:-8099}/ > /dev/null 2>&1; then
            bashio::log.info "✅ Flask server is responding to requests"
            bashio::log.info "Web UI should now be accessible via 'OPEN WEB UI' button"
        else
            bashio::log.warning "⚠️  Flask server is running but not responding yet"
            bashio::log.info "Web UI should be accessible via 'OPEN WEB UI' button"
        fi
    else
        bashio::log.error "❌ Flask server failed to start!"
        bashio::log.error "Check add-on logs for Python errors"
        exit 1
    fi
    
    # Keep running to allow web setup
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
