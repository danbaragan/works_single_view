FROM python:3.7-slim

RUN apt-get -y update &&\
    apt-get -y --no-install-recommends install \
    curl \
    gnupg2 \
    gcc \
    build-essential \
    vim \
    sudo \
    netcat-traditional \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


RUN adduser --disabled-password --gecos '' --shell /bin/false web &&\
    adduser web sudo &&\
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN mkdir -p /home/web/instance
RUN mkdir -p /home/web/bin
RUN mkdir -p /home/web/app

ENV HOME=/home/web \
    PATH=/home/web/bin:$PATH \
    USER=web

ADD web/ $HOME/app/

ADD build/common.sh \
    $HOME/bin/

WORKDIR $HOME/app
