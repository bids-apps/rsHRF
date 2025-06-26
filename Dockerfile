FROM python:3.6

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    curl \
                    bzip2 \
                    ca-certificates \
                    xvfb \
                    cython3 \
                    build-essential \
                    autoconf \
                    libtool \
                    pkg-config \
                    dc \
                    bc \
                    libgsl-dev && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN python -m pip install --no-cache-dir --upgrade pip setuptools && \
    python -m pip install --no-cache-dir setuptools_scm && \
    python -m pip install --no-cache-dir wheel && \
    python -m pip install --no-cache-dir cython && \
    python -m pip install --no-cache-dir numpy && \
    python -m pip install --no-cache-dir nibabel && \
    python -m pip install --no-cache-dir matplotlib && \
    python -m pip install --no-cache-dir scipy && \
    python -m pip install --no-cache-dir pybids==0.11.1 && \
    python -m pip install --no-cache-dir pandas && \
    python -m pip install --no-cache-dir patsy && \
    python -m pip install --no-cache-dir mpld3 && \
    python -m pip install --no-cache-dir duecredit && \
    python -m pip install --no-cache-dir joblib && \
    python -m pip install --no-cache-dir PyWavelets \
    && rm -rf ~/.cache/pip

RUN python -m pip install .
RUN python -m pip install --no-cache-dir --upgrade pip setuptools

WORKDIR /rsHRF
COPY . /rsHRF/

RUN python -m pip install --no-cache-dir -e .

ENTRYPOINT ["rsHRF"]
