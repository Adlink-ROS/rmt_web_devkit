# rmt_web_devkit

The Web example for ADLINK ROS Management Tool (RMT) on Ubuntu 20.04

## **Frontend**

### SOP:

Install the tools and packages for development

    ```bash
    sudo apt update
    sudo apt install -y git npm
    ```
Download this repo and install dependent packages

    ```bash
    cd $HOME
    git clone https://github.com/QQting/rmt_web_devkit.git
    cd $HOME/rmt_web_devkit/frontend
    npm install
    ```
Start the frontend

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

### Option 2 - Setup the Env on host:

Install the tools and packages for development

    ```bash
    sudo apt update
    sudo apt install -y git python-is-python3 curl
    ```

Download this repo and install dependent packages

    ```bash
    cd $HOME
    git clone https://github.com/QQting/rmt_web_devkit.git

    cd $HOME/rmt_web_devkit/backend/lib
    sudo dpkg -i *.deb

    cd $HOME/rmt_web_devkit/backend/app
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
    poetry install
    ```

Start the backend

```bash
cd $HOME/rmt_web_devkit/backend
./start_backend.sh
```

The default login account/password is ros/adlinkros.

## Development notes

- Username/password of FastaPI

    To change the default username and password of FastAPI server, please modify below codes in the file ```backend/app/app/core/security.py```

    ```py
    fake_users_db = {
        "ros": {
            "username": "ros",
            "full_name": "ros",
            "email": "ros@example.com",
            "hashed_password": "$2b$12$5Yy4jwGIXsbwM9NMaWloPOfKDsVE2YBH/Uqjrorl28zRY032BcRDu",
            "disabled": False,
        }
    }
    ```