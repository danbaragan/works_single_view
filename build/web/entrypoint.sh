#!/usr/bin/env bash

. common.sh

init() {
    flask init-db
    flask collect
}

if [ "$1" == "run" ]; then
    wait_service postgres 5432
    exec gunicorn \
        -w 2 \
        --forwarded-allow-ips="*" \
        -b ${FLASK_HOST-127.0.0.1}:${FLASK_PORT-5000} \
        "${FLASK_APP}:create_app()"

elif [ "$1" == "debug" ]; then
    wait_service postgres 5432
    exec flask run -h 0.0.0.0

elif [ "$1" == "init" ]; then
    init

else
    exec "$@"
fi
