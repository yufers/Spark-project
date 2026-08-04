FROM apache/spark:3.5.1-python3

USER root

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

RUN wget https://www.python.org/ftp/python/3.12.11/Python-3.12.11.tgz \
    && tar xzf Python-3.12.11.tgz \
    && cd Python-3.12.11 \
    && ./configure --enable-optimizations --with-ensurepip=install \
    && make -j$(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.12.11 Python-3.12.11.tgz

RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.12 1 \
    && update-alternatives --set python3 /usr/local/bin/python3.12

ENV PYSPARK_PYTHON=/usr/local/bin/python3.12
ENV PYSPARK_DRIVER_PYTHON=/usr/local/bin/python3.12

RUN /usr/local/bin/python3.12 -m pip install --upgrade pip setuptools wheel \
    && /usr/local/bin/python3.12 -m pip install valkey redis pyspark==3.5.1

ENV ICEBERG_VERSION=1.5.2
ENV AWS_SDK_VERSION=1.12.262
ENV HADOOP_AWS_VERSION=3.3.4

RUN wget -P /opt/spark/jars/ https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/${ICEBERG_VERSION}/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar && \
    wget -P /opt/spark/jars/ https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/${HADOOP_AWS_VERSION}/hadoop-aws-${HADOOP_AWS_VERSION}.jar && \
    wget -P /opt/spark/jars/ https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/${AWS_SDK_VERSION}/aws-java-sdk-bundle-${AWS_SDK_VERSION}.jar

USER spark