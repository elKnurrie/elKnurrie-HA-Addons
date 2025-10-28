#!/usr/bin/env bash

set -e

CONFIG_FILE=/data/options.json

ICLOUD_WEBDAV_URL=$(jq --raw-output '.icloud_webdav_url' "$CONFIG_FILE")
ICLOUD_USERNAME=$(jq --raw-output '.icloud_username' "$CONFIG_FILE")
ICLOUD_PASSWORD=$(jq --raw-output '.icloud_password' "$CONFIG_FILE")
BACKUP_SOURCE=$(jq --raw-output '.backup_source' "$CONFIG_FILE")
BACKUP_DESTINATION=$(jq --raw-output '.backup_destination' "$CONFIG_FILE")
RETENTION_DAYS=$(jq --raw-output '.retention_days' "$CONFIG_FILE")

mkdir -p "$BACKUP_DESTINATION"

# Configure rclone remote
mkdir -p /root/.config/rclone
cat <<EOF > /root/.config/rclone/rclone.conf
icloud:
    type = webdav
    url = $ICLOUD_WEBDAV_URL
    vendor = other
    user = $ICLOUD_USERNAME
    pass = $ICLOUD_PASSWORD
EOF

# Mount iCloud (background)
rclone mount icloud: "$BACKUP_DESTINATION" --daemon --timeout 10m --poll-interval 15s --vfs-cache-mode writes

echo "Waiting for mount to stabilize..."
sleep 15

# Sync Home Assistant backups to iCloud
echo "Syncing from $BACKUP_SOURCE to iCloud backup folder"
rclone copy "$BACKUP_SOURCE" icloud:backup-home-assistant-backups --verbose

# Remove old backups from iCloud
if [ "$RETENTION_DAYS" -gt 0 ]; then
  echo "Removing backups older than $RETENTION_DAYS days on iCloud"
  rclone delete --min-age ${RETENTION_DAYS}d icloud:backup-home-assistant-backups
fi

echo "Backup sync complete. Add-on will now wait."

# Keep addon running
tail -f /dev/null
