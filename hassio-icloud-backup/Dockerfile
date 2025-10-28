ARG BUILD_FROM=ghcr.io/home-assistant/base:latest
FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN apk add --no-cache curl bash py3-pip jq
RUN pip3 install --no-cache-dir pyyaml

# Install rclone
RUN curl https://rclone.org/install.sh | bash

COPY run.sh /run.sh
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
