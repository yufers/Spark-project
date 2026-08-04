FROM apache/spark:3.5.1-python3

USER root

# Зависимости для сборки Python из исходников
RUN apt-get update && apt-get install -y \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Скачиваем и собираем Python 3.12.11
RUN wget https://www.python.org/ftp/python/3.12.11/Python-3.12.11.tgz \
    && tar xzf Python-3.12.11.tgz \
    && cd Python-3.12.11 \
    && ./configure --enable-optimizations --with-ensurepip=install \
    && make -j$(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.12.11 Python-3.12.11.tgz

# Делаем python3 указывающим на 3.12
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.12 1 \
    && update-alternatives --set python3 /usr/local/bin/python3.12

# PySpark смотрит на PYSPARK_PYTHON — важно задать явно
ENV PYSPARK_PYTHON=/usr/local/bin/python3.12
ENV PYSPARK_DRIVER_PYTHON=/usr/local/bin/python3.12

# Устанавливаем pip и необходимые библиотеки в собранный Python 3.12
RUN /usr/local/bin/python3.12 -m pip install --upgrade pip setuptools wheel \
    && /usr/local/bin/python3.12 -m pip install valkey redis pyspark==3.5.1

USER spark