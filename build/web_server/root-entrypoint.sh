#!/bin/bash

wait_service() {
    while ! nc -z $1 $2; do
        echo "Waiting for $1 server to listen on port $2 ..."
        sleep 1
    done
}

CONFIGTEMPLATE=/etc/nginx/conf.d/nginx.conf.template
CONFIGFILE=/etc/nginx/conf.d/default.conf
python -c 'import os
import sys
import jinja2
sys.stdout.write(
    jinja2.Template(sys.stdin.read()
).render(env=os.environ))' <$CONFIGTEMPLATE >$CONFIGFILE


if [ "$1" == "run" ]; then
    wait_service web ${FLASK_PORT}
    exec nginx -g 'daemon off;'
elif [ "$1" == "debug" ]; then
    cat /etc/nginx/conf.d/default.conf
    wait_service web ${FLASK_PORT}
    exec nginx-debug -g 'daemon off;'
fi
