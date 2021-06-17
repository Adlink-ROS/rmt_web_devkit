#!/bin/bash

version=`cat version.txt`
echo -n "Do you want to uninstall the RMT server? (y/N) "
read answer
if [ "$answer" '==' "y" ] || [ "$answer" '==' "Y" ]; then
    sudo docker rmi rmt-frontend:${version}
    sudo docker rmi rmt-backend:${version}
else
    echo "Do nothing"
fi
