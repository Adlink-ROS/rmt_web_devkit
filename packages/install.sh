#!/bin/bash

version=`cat version.txt`
echo -n "Do you want to install the RMT webserver ${version}? (y/N) "
read answer
if [ "$answer" '==' "y" ] || [ "$answer" '==' "Y" ]; then
    sudo apt install docker.io
    sudo docker build -t rmt-frontend:${version} -f Dockerfile_frontend .
    sudo docker build -t rmt-backend:${version} -f Dockerfile_backend .
else
    echo "Do nothing"
fi
