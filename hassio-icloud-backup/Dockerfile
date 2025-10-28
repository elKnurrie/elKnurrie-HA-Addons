ARG BUILD_FROM
FROM $BUILD_FROM

# Install packages and dependencies
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        py3-requests \
        py3-six \
        py3-tzlocal \
        py3-pytz \
        bash \
        jq \
    && pip3 install --break-system-packages \
        pyicloud-ipd \
        setuptools

# Copy data for add-on
COPY run.py /
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
