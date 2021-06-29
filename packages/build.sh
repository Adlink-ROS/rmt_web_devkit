#!/bin/bash

version=`cat version.txt`
echo -n "Do you want to build the RMT webserver ${version}? (y/N) "
read answer
if [ "$answer" '==' "y" ] || [ "$answer" '==' "Y" ]; then
    sudo apt install docker.io
    sudo docker build -t rmt-frontend:${version} --build-arg RMT_VER=${version} -f Dockerfile_frontend .
    sudo docker build -t rmt-backend:${version} --build-arg RMT_VER=${version} -f Dockerfile_backend .
    sudo cp rmt-server /usr/bin/rmt-server
    sudo sed -i "s/vx.x.x/${version}/g" /usr/bin/rmt-server
    sudo sed -i "s/my_frontend_name/rmt-frontend/g" /usr/bin/rmt-server
    sudo sed -i "s/my_backend_name/rmt-backend/g" /usr/bin/rmt-server
else
    echo "Do nothing"
fi
