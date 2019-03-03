#!/bin/bash

wait_service() {
    while ! nc -z $1 $2; do
        echo "Waiting for $1 server to listen on port $2 ..."
        sleep 1
    done
}
