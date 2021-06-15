#!/bin/bash

if [ "$1" = "stop" ]; then
    echo "Stop the RMT server"
    sudo docker stop -t 1 rmt-frontend-container
    sudo docker stop -t 1 rmt-backend-container
elif [ "$1" = "start" ]; then
    echo "Start the RMT server"
    sudo docker run -d -p 9527:9527 --network=host --rm --name rmt-frontend-container rmt-frontend
    sudo docker run -d -p 8080:8080 --network=host --rm --name rmt-backend-container rmt-backend
else
    echo "Usage: ./rmt_server.sh [command]"
    echo "command:"
    echo "- start: run the server"
    echo "- stop:  stop the server"
fi
