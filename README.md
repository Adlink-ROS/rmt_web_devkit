# rmt_web_devkit

The Web example for ADLINK ROS Management Tool (RMT) on Ubuntu 20.04

## **Frontend**

### Prepare for the development environment:

1. Install the tools and packages for development

    ```bash
    sudo apt update
    sudo apt install -y git npm
    ```

2. Download this repo and install dependent packages

    ```bash
    cd $HOME
    git clone https://github.com/QQting/rmt_web_devkit.git
    cd $HOME/rmt_web_devkit/frontend
    npm install
    ```
### SOP to start the frontend:

```bash
cd $HOME/rmt_web_devkit/frontend
./start_frontend.sh
```

## **Backend**

There are two optons you can choose for the backend:

### Option 1 - Docker container

Build image from Dockerfile:

```bash
wget https://raw.githubusercontent.com/QQting/rmt_web_devkit/main/backend/Dockerfile
docker build -t="rmt-backend" . 
```

Start the container from the built image:

```bash
docker run -it -p 8080:8080 --network=host --rm rmt-backend
```

Start the backend in the container:

```bash
cd /root/rmt_web_devkit/backend
./start_backend.sh
```

Then, open the URL in the host browser

```bash
http://0.0.0.0:8080/docs
```

Now, you can test the RESTful API.

### Option 2 - Prepare for the development environment:

1. Install the tools and packages for development

    ```bash
    sudo apt update
    sudo apt install -y git python-is-python3 curl
    ```

2. Download this repo and install dependent packages

    ```bash
    cd $HOME
    git clone https://github.com/QQting/rmt_web_devkit.git

    cd $HOME/rmt_web_devkit/backend/lib
    sudo dpkg -i *.deb

    cd $HOME/rmt_web_devkit/backend/app
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
    poetry install
    ```

### SOP to start the backend:

```bash
cd $HOME/rmt_web_devkit/backend
./start_backend.sh
```
