ARG BUILD_FROM=rogerfar/rdtclient:latest
FROM $BUILD_FROM

# Install required packages
RUN \
    apk add --no-cache \
        bash \
        jq \
        curl

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
