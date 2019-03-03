#!/usr/bin/env bash

init() {
    flask init-db
}

if [ "$1" == "run" ]; then
    [ -f instance/${DATABASE_URL} ] || init
    exec gunicorn \
        -w 2 \
        --forwarded-allow-ips="*" \
        -b ${FLASK_HOST-127.0.0.1}:${FLASK_PORT-5000} \
        "${FLASK_APP}:create_app()"

elif [ "$1" == "debug" ]; then
    [ -f instance/${DATABASE_URL} ] || init
    exec flask run -h 0.0.0.0

elif [ "$1" == "init" ]; then
    init

else
    exec "$@"
fi
