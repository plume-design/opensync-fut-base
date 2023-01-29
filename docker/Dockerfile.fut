ARG PARENT_IMAGE=""
FROM $PARENT_IMAGE:latest

# -- Install Package dependencies:
RUN apt-get update && \
 apt-get install -y \
 mosquitto \
 nginx \
 haproxy \
 iptables \
 iperf3 \
 gettext-base

# JDK required for Allure generation
RUN mkdir -p /usr/share/man/man1 && \
 apt-get install -y openjdk-8-jdk && \
 apt-get autoremove -y

RUN apt-get update && \
 apt-get install -y \
 sudo && rm -rf /var/lib/apt/lists/*
