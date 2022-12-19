ARG BUILD_FROM=ghcr.io/hassio-addons/base:12.2.7
FROM $BUILD_FROM

ARG BUILD_ARCH=amd64
RUN apk add --no-cache python3 py3-pip net-tools
RUN pip install --no-cache-dir --upgrade atcom

COPY rootfs/* /
RUN chmod a+x /run.sh

CMD [ "/run.sh"]