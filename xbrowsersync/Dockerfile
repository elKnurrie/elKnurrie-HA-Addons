ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    ca-certificates \
    gnupg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install MongoDB 7.0
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" > /etc/apt/sources.list.d/mongodb-org-7.0.list \
    && apt-get update \
    && apt-get install -y mongodb-org \
    && rm -rf /var/lib/apt/lists/*

# Setup directories
RUN mkdir -p /data/db /var/log/mongodb \
    && chown -R mongodb:mongodb /data /var/log/mongodb

# Download and setup xBrowserSync API
RUN curl -L -o /tmp/xbrowsersync.tar.gz https://github.com/xbrowsersync/api/archive/refs/tags/v1.1.13.tar.gz \
    && tar -xzf /tmp/xbrowsersync.tar.gz -C /opt \
    && mv /opt/api-1.1.13 /opt/xbrowsersync-api \
    && cd /opt/xbrowsersync-api \
    && npm install --production --no-audit --no-fund --ignore-scripts \
    && rm -rf /tmp/xbrowsersync.tar.gz

# Copy configuration
COPY settings.json /opt/xbrowsersync-api/config/settings.json
COPY run.sh /opt/xbrowsersync-api/run.sh
RUN chmod +x /opt/xbrowsersync-api/run.sh

WORKDIR /opt/xbrowsersync-api

# Expose API port
EXPOSE 8080

CMD ["./run.sh"]
