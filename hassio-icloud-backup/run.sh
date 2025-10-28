#!/usr/bin/with-contenv bashio

set -e

CONFIG_FILE=/data/options.json

ICLOUD_USERNAME=$(jq --raw-output '.icloud_username' "$CONFIG_FILE")
ICLOUD_PASSWORD=$(jq --raw-output '.icloud_password' "$CONFIG_FILE")
ICLOUD_2FA_CODE=$(jq --raw-output '.icloud_2fa_code // empty' "$CONFIG_FILE")
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
    bashio::log.info "Please open the Web UI to complete 2FA authentication:"
    bashio::log.info "  1. Click 'OPEN WEB UI' button in the add-on page"
    bashio::log.info "  2. Enter your 2FA code when prompted"
    bashio::log.info "  3. Restart this add-on after authentication"
    bashio::log.info ""
    bashio::log.info "Starting web interface..."
    
    # Start the web setup interface with proper error handling
    python3 /setup_server.py 2>&1 | while IFS= read -r line; do
        bashio::log.info "$line"
    done &
    
    # Wait a moment for server to start
    sleep 2
    bashio::log.info "Web UI should now be accessible via 'OPEN WEB UI' button"
    
    # Keep running to allow web setup
    tail -f /dev/null
fi

bashio::log.info "Using saved iCloud session..."

# Create rclone config
cat > /root/.config/rclone/rclone.conf <<EOF
[icloud]
type = iclouddrive
user = $ICLOUD_USERNAME
pass = $(rclone obscure "$ICLOUD_PASSWORD")
trust_token = $(cat /data/icloud_trust_token.txt 2>/dev/null || echo "")
session_token = $(cat /data/icloud_session_token.txt 2>/dev/null || echo "")
EOF

bashio::log.info "Testing iCloud Drive connection..."

if ! rclone lsd icloud: --verbose 2>&1 | tee /tmp/rclone-debug.log; then
    bashio::log.error "Failed to connect to iCloud Drive."
    bashio::log.error "Session may have expired. Please re-authenticate:"
    bashio::log.info "1. Delete /data/icloud_session_configured"
    bashio::log.info "2. Restart add-on to trigger setup again"
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
