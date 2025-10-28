ARG BUILD_FROM
FROM $BUILD_FROM

# Install rclone and dependencies
RUN \
    apk add --no-cache \
        bash \
        jq \
        curl \
        ca-certificates \
        unzip \
    && curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip \
    && unzip -o rclone-current-linux-amd64.zip \
    && cd rclone-*-linux-amd64 \
    && cp rclone /usr/bin/ \
    && chmod 755 /usr/bin/rclone \
    && cd .. \
    && rm -rf rclone-*

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
