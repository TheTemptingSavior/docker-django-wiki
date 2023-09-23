FROM ghcr.io/linuxserver/baseimage-alpine:3.18

# packages as variables
ARG BUILD_PACKAGES="gcc python3-dev build-base linux-headers pcre-dev"
ARG RUNTIME_PACKAGES="\
    python3 py3-pip \
    nginx curl \
    libjpeg jpeg-dev libpng libpng-dev"

COPY root/requirements.txt /

RUN \
 if [ -n "${BUILD_PACKAGES}" ]; then \
    echo "**** install build packages ****" && \
    apk add --no-cache \
        --virtual=build-dependencies \
        $BUILD_PACKAGES; \
 fi && \
 if [ -n "${RUNTIME_PACKAGES}" ]; then \
    echo "**** install runtime packages ****" && \
    apk add --no-cache \
        $RUNTIME_PACKAGES; \
 fi && \
 pip3 --no-cache install -r /requirements.txt && \
 echo "**** cleanup ****" && \
 if [ -n "${BUILD_PACKAGES}" ]; then \
    apk del --purge \
        build-dependencies; \
 fi && \
 rm -rf \
    /root/.cache \
    /tmp/*

# copy local files
COPY root /

EXPOSE 80
VOLUME /config