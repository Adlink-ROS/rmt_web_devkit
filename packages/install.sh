#!/bin/bash

echo -n "Do you want to install the RMT server? (y/N) "
read answer
if [ "$answer" '==' "y" ] || [ "$answer" '==' "Y" ]; then
    sudo apt install docker.io
    sudo docker build -t rmt-frontend -f Dockerfile_frontend .
    sudo docker build -t rmt-backend -f Dockerfile_backend .
else
    echo "Do nothing"
fi
