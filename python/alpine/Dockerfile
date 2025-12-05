FROM alpine:3.22.1
RUN apk --no-cache upgrade && \
    apk --no-cache add --virtual .build-deps build-base python3-dev libffi-dev openssl-dev && \
    apk --no-cache add py3-pip && \
    pip3 install --break-system-packages --upgrade pip setuptools && \
    apk del .build-deps && \
    rm -rf /root/.cache/pip/*