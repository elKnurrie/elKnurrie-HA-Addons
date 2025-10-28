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
        py3-pip \
        py3-flask \
    && curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip \
    && unzip -o rclone-current-linux-amd64.zip \
    && cd rclone-*-linux-amd64 \
    && cp rclone /usr/bin/ \
    && chmod 755 /usr/bin/rclone \
    && cd .. \
    && rm -rf rclone-* \
    && pip3 install --break-system-packages flask

# Copy add-on files
COPY setup_server.py /
COPY run.sh /
RUN chmod a+x /run.sh /setup_server.py

# Expose port for setup web interface
EXPOSE 8099

CMD [ "/run.sh" ]
