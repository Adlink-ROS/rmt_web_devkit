# rmt_web_devkit

This is Web example for ADLINK Robot Management Tool (RMT) on Ubuntu 20.04

# Usage

* Download source code

```
sudo apt update && sudo apt install -y git curl
cd $HOME
git clone https://github.com/Adlink-ROS/rmt_web_devkit.git
```

## Frontend

* Install necessary packages

```bash
# Install nodejs (you can use your own way to install, for example, nvm)
curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt-get install -y nodejs
```

* Install dependent packages

```bash
cd $HOME/rmt_web_devkit/frontend
npm install
```

* Run the frontend

```bash
cd $HOME/rmt_web_devkit/frontend
./start_frontend.sh
```

## Backend

* Install necessary packages

```bash
sudo apt install -y python3.8-dev
sudo apt install -y libcairo2-dev libgirepository1.0-dev libnm-dev
# install poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
# Add poetry binary to path
echo 'export PATH="$HOME/.poetry/bin:$PATH"' >> ~/.bashrc
```

* Install dependent packages

```bash
# Install RMT library
cd $HOME/rmt_web_devkit/backend/lib
sudo dpkg -i *.deb
# Install poetry
cd $HOME/rmt_web_devkit/backend/app
poetry env use $(which python3.8)
poetry install
```

* Run the backend

```bash
cd $HOME/rmt_web_devkit/backend
./start_backend.sh
```

The default login account/password is ros/adlinkros.

# Run with container

You can also use docker to run the RMT web server.

* Install RMT web server.
  - It'll take a long time.

```bash
cd $HOME/rmt_web_devkit/packages
./install.sh
```

* Start/Stop the web server

```bash
# start
rmt-server start
# stop
rmt-server stop
# show status
rmt-server status
```

* Uninstall the web server

```bash
rmt-server uninstall
```

# Development notes

Please go to the online user manual for more development information.

https://github.com/Adlink-ROS/RMT-User-Manual/wiki/Web-Development#web-development-notes
