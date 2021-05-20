import os

# TO SUPPORT RUN python main.py in windows,but I use python "app/main.py" to start in liunx
os.sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import fastapi
from fastapi import routing, FastAPI
from app.extensions.routing import APIRouter as MyAPIRouter, APIRoute as MyAPIRoute

# rewrite APIRouter and APIRoute and add parameter exclude_dependencies to deny global dependencies
fastapi.APIRouter = routing.APIRouter = MyAPIRouter
fastapi.APIRoute = routing.APIRoute = MyAPIRoute

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.api.api_v1.websocket import socket_app
from app.middleware import register_middleware
import rmt_py_wrapper

# app
app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
# set middleware
register_middleware(app)

# set router
app.include_router(api_router, prefix=settings.API_V1_STR)
# set socketio
app.mount('/', socket_app)

if __name__ == '__main__':
    import uvicorn
    rmt_py_wrapper.rmt_server_init()
    uvicorn.run(app='main:app', host="0.0.0.0", port=8080)
    rmt_py_wrapper.rmt_server_deinit()
