#!/bin/bash
set -e

# Read options from Home Assistant addon config
CONFIG_PATH=/data/options.json
if [ -f "$CONFIG_PATH" ]; then
    DB_PASSWORD=$(jq -r '.db_password // empty' "$CONFIG_PATH")
    API_PORT=$(jq -r '.api_port // 8913' "$CONFIG_PATH")
else
    DB_PASSWORD="${DB_PASSWORD:-}"
    API_PORT="${API_PORT:-8913}"
fi

echo "DB_PASSWORD is set: $([ -n "$DB_PASSWORD" ] && echo 'yes' || echo 'no')"
echo "API_PORT: $API_PORT"

# Update settings.json with values
if [ -n "$DB_PASSWORD" ]; then
    sed -i "s/\"password\": \"\"/\"password\": \"$DB_PASSWORD\"/" /opt/xbrowsersync-api/config/settings.json
fi

# Update port if different
if [ "$API_PORT" != "8080" ]; then
    sed -i "s/\"port\": 8913/\"port\": $API_PORT/" /opt/xbrowsersync-api/config/settings.json
fi

# Create required directories
mkdir -p /data/db /var/log/mongodb
chown -R mongodb:mongodb /data /var/log/mongodb

# Start MongoDB in background
echo "Starting MongoDB..."
su -s /bin/bash mongodb -c "mongod --dbpath /data/db --logpath /var/log/mongodb/mongodb.log --fork --bind_ip 127.0.0.1"

# Wait for MongoDB to be ready
echo "Waiting for MongoDB..."
for i in {1..30}; do
    if mongosh --quiet --eval "db.adminCommand('ping')" 2>/dev/null; then
        echo "MongoDB is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "MongoDB failed to start!"
        cat /var/log/mongodb/mongodb.log
        exit 1
    fi
    echo "MongoDB not ready yet... ($i/30)"
    sleep 2
done

# Create database user if needed
echo "Setting up database user..."
if [ -n "$DB_PASSWORD" ]; then
    mongosh --quiet --eval "
        db = db.getSiblingDB('admin');
        try {
            db.createUser({
                user: 'xbrowsersync',
                pwd: '$DB_PASSWORD',
                roles: [{ role: 'readWrite', db: 'xbrowsersync' }]
            });
            print('User created successfully');
        } catch(e) {
            print('User may already exist (this is OK)');
        }
    " 2>/dev/null || echo "Skipping user creation"
fi

# Ensure xbrowsersync database exists
mongosh --quiet --eval "db = db.getSiblingDB('xbrowsersync');" 2>/dev/null || true

# Start xBrowserSync API (keep in foreground)
echo "Starting xBrowserSync API on port $API_PORT..."
cd /opt/xbrowsersync-api
node dist/api.js
