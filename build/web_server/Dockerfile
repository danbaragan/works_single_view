FROM nginx

RUN apt-get -y update &&\
    apt-get -y --no-install-recommends install \
    python-jinja2 \
    netcat-traditional \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ADD build/web_server/nginx.conf.template /etc/nginx/conf.d/
ADD build/web_server/root-entrypoint.sh \
    build/common.sh \
    /sbin/

ENTRYPOINT ["root-entrypoint.sh"]
CMD ["run"]
