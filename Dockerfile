FROM alpine:latest

ENV PACKAGES="\
    musl \
    libpng \
    libxml2 \
    libxslt \
    freetype \
    libstdc++ \
    openblas \
    "

ENV PYTHON_PACKAGES="\
    numpy \
    matplotlib \
    scipy \
    pandas \
    joblib \
    rsHRF \
    "

RUN apk add --no-cache --virtual build-dependencies python3 \
    && apk add --virtual build-runtime \
    g++ gfortran file binutils openblas-dev python3-dev gcc build-base libpng-dev \
    musl-dev freetype-dev libxml2-dev libxslt-dev pkgconfig \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && ln -sf pip3 /usr/bin/pip \
    && pip install --no-cache-dir $PYTHON_PACKAGES \
    && rm -r /root/.cache \
    && apk del build-runtime \
    && apk add --no-cache --virtual build-dependencies $PACKAGES \
    && rm -rf /var/cache/apk/*

ENTRYPOINT ["rsHRF"]
