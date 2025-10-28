ARG BUILD_FROM
FROM $BUILD_FROM

# Install Chromium and dependencies for browser automation
RUN \
    apk add --no-cache \
        chromium \
        chromium-chromedriver \
        python3 \
        py3-pip \
        bash \
        jq \
    && pip3 install --break-system-packages \
        selenium \
        webdriver-manager

# Copy data for add-on
COPY run.py /
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
