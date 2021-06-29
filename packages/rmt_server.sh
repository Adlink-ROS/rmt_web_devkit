#!/bin/bash

version=`cat version.txt`
if [ "$1" = "stop" ]; then
    echo "Stop the RMT server"
    sudo docker stop -t 1 rmt-frontend-container > /dev/null
    sudo docker stop -t 1 rmt-backend-container > /dev/null
elif [ "$1" = "start" ]; then
    echo "Start the RMT server"
    # Use port 9527
    sudo docker run -d -p 9527:9527 --rm --name rmt-frontend-container rmt-frontend:${version} > /dev/null
    # Use port 8080
    sudo docker run -d --privileged --volume /var/run/dbus:/var/run/dbus --network=host --rm --name rmt-backend-container rmt-backend:${version} > /dev/null
elif [ "$1" = "status" ]; then
    sudo echo -n "RMT server status: "
    frontend=`sudo docker ps -f status=running -f name=rmt-frontend-container --format "{{.Names}}"`
    backend=`sudo docker ps -f status=running -f name=rmt-backend-container --format "{{.Names}}"`
    if [ "$frontend" = "rmt-frontend-container" ] && [ "$backend" = "rmt-backend-container" ]; then
        echo "Running"
    else
        echo "Not Running"
    fi
else
    echo "Usage: ./rmt_server.sh [command]"
    echo "command:"
    echo "- start:  run the server"
    echo "- stop:   stop the server"
    echo "- status: show the server status"
fi
