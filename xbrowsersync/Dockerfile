ARG BUILD_FROM
FROM $BUILD_FROM

# Install MongoDB and dependencies
RUN apk add --no-cache \
    bash \
    curl \
    ca-certificates \
    mongodb \
    mongodb-tools \
    nodejs \
    npm

# Setup MongoDB data directory
RUN mkdir -p /data/db && chown -R mongodb:mongodb /data && \
    mkdir -p /var/log && chown mongodb:mongodb /var/log

# Download and setup xBrowserSync API
RUN curl -L -o /tmp/xbrowsersync.tar.gz https://github.com/xbrowsersync/api/archive/refs/tags/1.18.1.tar.gz && \
    tar -xzf /tmp/xbrowsersync.tar.gz -C /opt && \
    mv /opt/api-1.18.1 /opt/xbrowsersync-api && \
    cd /opt/xbrowsersync-api && \
    npm install --production --no-audit --no-fund && \
    rm -rf /tmp/xbrowsersync.tar.gz

# Copy configuration
COPY settings.json /opt/xbrowsersync-api/config/settings.json
COPY run.sh /opt/xbrowsersync-api/run.sh
RUN chmod +x /opt/xbrowsersync-api/run.sh

WORKDIR /opt/xbrowsersync-api

# Expose API port
EXPOSE 8080

CMD ["./run.sh"]
