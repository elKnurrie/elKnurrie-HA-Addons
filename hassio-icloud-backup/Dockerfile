ARG BUILD_FROM
FROM $BUILD_FROM

# Install packages and dependencies
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        py3-requests \
        bash \
        jq \
    && pip3 install --break-system-packages \
        pyicloud

# Copy data for add-on
COPY run.py /
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
