ARG BUILD_FROM
FROM $BUILD_FROM

# Install packages and dependencies
RUN \
    apk add --no-cache \
        curl \
        bash \
        jq \
        py3-yaml \
        python3 \
        fuse \
        ca-certificates \
        unzip \
        bind-tools \
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
