FROM ubuntu:22.04

LABEL Name="PySamp_Server"
LABEL Version="0.0.1"

EXPOSE 7777

ENV TZ="Europe/Budapest"
ENV OMP="/omp"
ENV MOD="/mod"
ENV SRV="/omp-srv"

RUN mkdir $OMP
RUN mkdir $MOD
RUN mkdir $SRV

VOLUME $OMP
VOLUME $MOD
VOLUME $SRV

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt -y update

RUN dpkg --add-architecture i386
RUN apt -y install software-properties-common

RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt -y update

RUN apt -y install gcc-i686-linux-gnu \
    g++-i686-linux-gnu \
    libc6:i386 \
    libstdc++6:i386 \
    wget \
    gettext-base \
    python3.12-dev:i386

RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.12 get-pip.py && \
    rm get-pip.py

RUN wget https://launchpad.net/ubuntu/+archive/primary/+files/libssl1.1_1.1.1-1ubuntu2.1~18.04.23_i386.deb && \
    dpkg -i libssl1.1_1.1.1-1ubuntu2.1~18.04.23_i386.deb && \
    rm libssl1.1_1.1.1-1ubuntu2.1~18.04.23_i386.deb

WORKDIR $OMP

RUN wget https://github.com/openmultiplayer/open.mp/releases/download/v1.4.0.2779/open.mp-linux-x86-dynssl.tar.gz -O server.tar.gz && \
    tar -xzf server.tar.gz && \
    mv Server/* . && \
    rm -rf Server && \
    rm server.tar.gz && \
    chmod +x omp-server

WORKDIR /

COPY docker_run.sh .

RUN  chmod +x docker_run.sh

CMD ["./docker_run.sh"]
