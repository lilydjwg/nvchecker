FROM python:3.8-alpine
LABEL description="New version checker for software"
ENV DEPENDENCIES libcurl wget gzip
ENV BUILD_DEPENDENCIES curl-dev build-base
ENV PYCURL_SSL_LIBRARY openssl

COPY . /app
RUN \
    cd /app && \
    apk add --no-cache --virtual .build-dependencies $BUILD_DEPENDENCIES  && \
    apk add --no-cache --virtual .dependencies $DEPENDENCIES && \
    python3 setup.py install && \
    apk --purge del .build-dependencies

CMD ["nvchecker"]
