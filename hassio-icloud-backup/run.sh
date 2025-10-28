#!/usr/bin/with-contenv bashio

set -e

CONFIG_FILE=/data/options.json

ICLOUD_WEBDAV_URL=$(jq --raw-output '.icloud_webdav_url' "$CONFIG_FILE")
ICLOUD_USERNAME=$(jq --raw-output '.icloud_username' "$CONFIG_FILE")
ICLOUD_PASSWORD=$(jq --raw-output '.icloud_password' "$CONFIG_FILE")
BACKUP_SOURCE=$(jq --raw-output '.backup_source' "$CONFIG_FILE")
BACKUP_DESTINATION=$(jq --raw-output '.backup_destination' "$CONFIG_FILE")
RETENTION_DAYS=$(jq --raw-output '.retention_days' "$CONFIG_FILE")

bashio::log.info "Starting iCloud Backup add-on..."

# Validate required configuration
if [ -z "$ICLOUD_USERNAME" ] || [ -z "$ICLOUD_PASSWORD" ]; then
    bashio::log.error "iCloud username and password are required!"
    exit 1
fi

mkdir -p "$BACKUP_DESTINATION"

# Configure rclone remote
bashio::log.info "Configuring rclone for iCloud WebDAV..."
mkdir -p /root/.config/rclone

# Obscure the password for rclone
OBSCURED_PASSWORD=$(rclone obscure "$ICLOUD_PASSWORD")

# Create rclone config (no indentation, proper format)
cat > /root/.config/rclone/rclone.conf <<EOF
[icloud]
type = webdav
url = $ICLOUD_WEBDAV_URL
vendor = other
user = $ICLOUD_USERNAME
pass = $OBSCURED_PASSWORD
EOF

bashio::log.info "Testing iCloud connection..."

# Test connection
if ! rclone lsd icloud: --max-depth 1 --verbose 2>&1 | tee /tmp/rclone-debug.log; then
    bashio::log.error "Failed to connect to iCloud WebDAV."
    bashio::log.error "Debug output:"
    cat /tmp/rclone-debug.log || true
    bashio::log.info ""
    bashio::log.info "Troubleshooting:"
    bashio::log.info "1. Use an app-specific password from https://appleid.apple.com"
    bashio::log.info "2. Enable 2-factor authentication"
    bashio::log.info "3. Enable iCloud Drive in your iCloud settings"
    bashio::log.info "4. Your Home Assistant has DNS issues - check Settings → System → Network"
    exit 1
fi

bashio::log.info "iCloud connection successful!"

# Sync Home Assistant backups to iCloud
bashio::log.info "Syncing backups from $BACKUP_SOURCE to iCloud..."
rclone sync "$BACKUP_SOURCE" icloud:backup-home-assistant --create-empty-src-dirs --verbose

# Remove old backups from iCloud
if [ "$RETENTION_DAYS" -gt 0 ]; then
    bashio::log.info "Removing backups older than $RETENTION_DAYS days from iCloud..."
    rclone delete --min-age ${RETENTION_DAYS}d icloud:backup-home-assistant --verbose
fi

bashio::log.info "Backup sync complete!"
bashio::log.info "Add-on will continue running and sync on restart."

# Keep addon running
tail -f /dev/null
