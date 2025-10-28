#!/usr/bin/with-contenv bashio

set -e

CONFIG_FILE=/data/options.json

ICLOUD_USERNAME=$(jq --raw-output '.icloud_username' "$CONFIG_FILE")
ICLOUD_PASSWORD=$(jq --raw-output '.icloud_password' "$CONFIG_FILE")
BACKUP_SOURCE=$(jq --raw-output '.backup_source' "$CONFIG_FILE")
ICLOUD_FOLDER=$(jq --raw-output '.icloud_folder' "$CONFIG_FILE")
RETENTION_DAYS=$(jq --raw-output '.retention_days' "$CONFIG_FILE")

bashio::log.info "Starting iCloud Backup add-on using rclone..."

# Validate required configuration
if [ -z "$ICLOUD_USERNAME" ] || [ -z "$ICLOUD_PASSWORD" ]; then
    bashio::log.error "iCloud username and password are required!"
    exit 1
fi

# Create rclone config directory
mkdir -p /root/.config/rclone

bashio::log.info "Configuring rclone for iCloud Drive..."

# Check if we already have a valid session token
if [ -f /data/rclone-icloud-session.txt ]; then
    bashio::log.info "Found existing iCloud session token"
    SESSION_TOKEN=$(cat /data/rclone-icloud-session.txt)
else
    bashio::log.warning "No session token found. First-time setup required."
    bashio::log.info "Please run: rclone config to set up iCloud Drive"
    bashio::log.info "After setup, the session token will be saved for future use"
    SESSION_TOKEN=""
fi

# Create rclone config for iCloud Drive
cat > /root/.config/rclone/rclone.conf <<EOF
[icloud]
type = iclouddrive
user = $ICLOUD_USERNAME
pass = $(rclone obscure "$ICLOUD_PASSWORD")
session_token = $SESSION_TOKEN
EOF

bashio::log.info "Testing iCloud Drive connection..."

# Test connection - this may prompt for 2FA on first run
if ! rclone lsd icloud: --verbose 2>&1 | tee /tmp/rclone-debug.log; then
    bashio::log.error "Failed to connect to iCloud Drive."
    bashio::log.error ""
    bashio::log.error "Debug output:"
    cat /tmp/rclone-debug.log || true
    bashio::log.info ""
    bashio::log.info "If you see 2FA errors, you need to:"
    bashio::log.info "1. Run this command in the add-on terminal:"
    bashio::log.info "   rclone config"
    bashio::log.info "2. Follow the prompts to authenticate with 2FA"
    bashio::log.info "3. The session token will be saved automatically"
    bashio::log.info "4. Restart the add-on"
    exit 1
fi

# Save session token for next time if it changed
NEW_SESSION=$(rclone config show icloud | grep session_token | cut -d'=' -f2- | xargs)
if [ -n "$NEW_SESSION" ] && [ "$NEW_SESSION" != "$SESSION_TOKEN" ]; then
    echo "$NEW_SESSION" > /data/rclone-icloud-session.txt
    bashio::log.info "Session token saved for future use"
fi

bashio::log.info "iCloud Drive connection successful!"

# Sync backups to iCloud Drive
bashio::log.info "Syncing backups from $BACKUP_SOURCE to iCloud Drive..."
rclone sync "$BACKUP_SOURCE" "icloud:$ICLOUD_FOLDER" --create-empty-src-dirs --verbose

# Remove old backups
if [ "$RETENTION_DAYS" -gt 0 ]; then
    bashio::log.info "Removing backups older than $RETENTION_DAYS days..."
    rclone delete --min-age ${RETENTION_DAYS}d "icloud:$ICLOUD_FOLDER" --verbose
fi

bashio::log.info "Backup sync complete!"
bashio::log.info "Add-on will continue running and sync on restart."

# Keep addon running
tail -f /dev/null
