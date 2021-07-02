#!/bin/bash

version=`cat version.txt`
echo -n "Do you want to install the RMT webserver ${version}? (y/N) "
read answer
if [ "$answer" '==' "y" ] || [ "$answer" '==' "Y" ]; then
    sudo apt install docker.io
    sudo docker pull adlinkrmt/rmt-frontend:${version}
    sudo docker pull adlinkrmt/rmt-backend:${version}
    sudo cp rmt-server /usr/bin/rmt-server
    sudo sed -i "s/vx.x.x/${version}/g" /usr/bin/rmt-server
    sudo sed -i "s/my_frontend_name/adlinkrmt\/rmt-frontend/g" /usr/bin/rmt-server
    sudo sed -i "s/my_backend_name/adlinkrmt\/rmt-backend/g" /usr/bin/rmt-server
else
    echo "Do nothing"
fi
