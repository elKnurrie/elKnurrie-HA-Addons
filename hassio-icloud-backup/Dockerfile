ARG BUILD_FROM
FROM $BUILD_FROM

# Install rclone, Python, and dependencies
RUN \
    apk add --no-cache \
        bash \
        jq \
        curl \
        ca-certificates \
        unzip \
        python3 \
    && curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip \
    && unzip -o rclone-current-linux-amd64.zip \
    && cd rclone-*-linux-amd64 \
    && cp rclone /usr/bin/ \
    && chmod 755 /usr/bin/rclone \
    && cd .. \
    && rm -rf rclone-*

# Copy add-on files
COPY auth_api.py /
COPY run.sh /
RUN chmod a+x /run.sh /auth_api.py

# Expose port for setup web interface
EXPOSE 8099

CMD [ "/run.sh" ]
