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
    && curl https://rclone.org/install.sh | bash

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
