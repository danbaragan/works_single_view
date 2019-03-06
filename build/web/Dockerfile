FROM python:3.7-slim

RUN apt-get -y update &&\
    apt-get -y --no-install-recommends install \
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

ENV HOME=/home/web \
    PATH=/home/web/bin:$PATH \
    USER=web

ADD web/ $HOME/
ADD build/web/requirements.txt \
    build/web/requirements.dev.txt \
    $HOME/

WORKDIR $HOME
# TODO make another image, based on this one, for development
RUN pip install -r requirements.dev.txt

ADD build/web/entrypoint.sh \
    build/common.sh \
    $HOME/bin/

RUN chown -R web:web $HOME

USER $USER
VOLUME ["${HOME}/instance"]
ENTRYPOINT ["entrypoint.sh"]
CMD ["run"]
