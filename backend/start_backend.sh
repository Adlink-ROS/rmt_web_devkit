#!/bin/bash

WORK_DIR=$PWD
cd $WORK_DIR/app
poetry run python app/main.py -i 0.0.0.0 -p 8080
