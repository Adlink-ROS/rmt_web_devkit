#!/bin/bash

echo -n "Do you want to uninstall the RMT server? (y/N) "
read answer
if [ "$answer" '==' "y" ] || [ "$answer" '==' "Y" ]; then
    sudo docker rmi rmt-frontend
else
    echo "Do nothing"
fi
