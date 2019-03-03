#!/bin/bash

. common.sh

CONFIGTEMPLATE=/etc/nginx/conf.d/nginx.conf.template
CONFIGFILE=/etc/nginx/conf.d/default.conf
python -c 'import os
import sys
import jinja2
sys.stdout.write(
    jinja2.Template(sys.stdin.read()
).render(env=os.environ))' <$CONFIGTEMPLATE >$CONFIGFILE


if [ "$1" == "run" ]; then
    exec nginx -g 'daemon off;'
elif [ "$1" == "debug" ]; then
    cat /etc/nginx/conf.d/default.conf
    exec nginx-debug -g 'daemon off;'
fi
