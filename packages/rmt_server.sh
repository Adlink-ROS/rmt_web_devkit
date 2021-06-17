#!/bin/bash

version=`cat version.txt`
if [ "$1" = "stop" ]; then
    echo "Stop the RMT server"
    sudo docker stop -t 1 rmt-frontend-container
    sudo docker stop -t 1 rmt-backend-container
elif [ "$1" = "start" ]; then
    echo "Start the RMT server"
    # Use port 9527
    sudo docker run -d -p 9527:9527 --rm --name rmt-frontend-container rmt-frontend:${version}
    # Use port 8080
    sudo docker run -d --privileged --volume /var/run/dbus:/var/run/dbus --network=host --rm --name rmt-backend-container rmt-backend:${version}
else
    echo "Usage: ./rmt_server.sh [command]"
    echo "command:"
    echo "- start: run the server"
    echo "- stop:  stop the server"
fi
