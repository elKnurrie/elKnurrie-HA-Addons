#!/bin/bash
set -e

# Get password from options or environment
DB_PASSWORD="${DB_PASSWORD:-${DB_PWD:-}}"
API_PORT="${API_PORT:-8080}"

# Update settings.json with values
if [ -n "$DB_PASSWORD" ]; then
    sed -i "s/\"password\": \"\"/\"password\": \"$DB_PASSWORD\"/" /opt/xbrowsersync-api/config/settings.json
fi

# Update port if different
if [ "$API_PORT" != "8080" ]; then
    sed -i "s/\"port\": 8080/\"port\": $API_PORT/" /opt/xbrowsersync-api/config/settings.json
fi

# Create required directories
mkdir -p /data/db /var/log
chown -R mongodb:mongodb /data /var/log

# Start MongoDB in background
echo "Starting MongoDB..."
su -s /bin/bash mongodb -c "mongod --dbpath /data/db --logpath /var/log/mongodb.log --fork --bind_ip 127.0.0.1"

# Wait for MongoDB to be ready
echo "Waiting for MongoDB..."
for i in {1..30}; do
    if mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1 || mongo --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        echo "MongoDB is ready!"
        break
    fi
    echo "MongoDB not ready yet... ($i/30)"
    sleep 2
done

# Create database user if needed
echo "Setting up database user..."
if [ -n "$DB_PASSWORD" ]; then
    (mongosh --eval "
        db = db.getSiblingDB('admin');
        try {
            db.createUser({
                user: 'xbrowsersync',
                pwd: '$DB_PASSWORD',
                roles: [{ role: 'readWrite', db: 'xbrowsersync' }]
            });
            print('User created successfully');
        } catch(e) {
            print('User may already exist: ' + e.message);
        }
    " 2>/dev/null || true) || \
    (mongo --eval "
        db = db.getSiblingDB('admin');
        try {
            db.createUser({
                user: 'xbrowsersync',
                pwd: '$DB_PASSWORD',
                roles: [{ role: 'readWrite', db: 'xbrowsersync' }]
            });
            print('User created successfully');
        } catch(e) {
            print('User may already exist: ' + e.message);
        }
    " 2>/dev/null || true)
fi

# Create xbrowsersync database
(mongosh --eval "db = db.getSiblingDB('xbrowsersync');" 2>/dev/null || true) || \
(mongo --eval "db = db.getSiblingDB('xbrowsersync');" 2>/dev/null || true)

# Start xBrowserSync API
echo "Starting xBrowserSync API..."
cd /opt/xbrowsersync-api
npm start
