#!/usr/bin/with-contenv bashio

set -e

CONFIG_FILE=/data/options.json

# Read download path from options
DOWNLOAD_PATH=$(jq --raw-output '.download_path // "/share/rdt-downloads"' "$CONFIG_FILE")

# Validate path starts with /share
if [[ ! "$DOWNLOAD_PATH" == /share/* ]]; then
    bashio::log.warning "Download path must be under /share. Using default: /share/rdt-downloads"
    DOWNLOAD_PATH="/share/rdt-downloads"
fi

# Create download directory
mkdir -p "$DOWNLOAD_PATH"
chmod 755 "$DOWNLOAD_PATH"

bashio::log.info "Download path configured as: $DOWNLOAD_PATH"

# Export environment variables that rdt-client might use
export DOWNLOAD_PATH="$DOWNLOAD_PATH"
export TZ="${TZ:-Europe/Amsterdam}"

bashio::log.info "Starting RDT Client..."

# Start rdt-client (delegate to original entrypoint if it exists)
if [ -x "/init" ]; then
    exec /init
elif [ -x "/app/rdt-client" ]; then
    exec /app/rdt-client
else
    bashio::log.error "RDT Client binary not found!"
    exit 1
fi
