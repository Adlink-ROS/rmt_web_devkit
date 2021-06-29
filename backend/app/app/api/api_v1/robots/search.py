from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.extensions.utils import list_to_tree
import rmt_py_wrapper
import json

router = APIRouter()

def rmt_discovery():
    num_ptr = rmt_py_wrapper.new_intptr()
    dev_list = rmt_py_wrapper.device_info_list.frompointer(rmt_py_wrapper.rmt_server_create_device_list(num_ptr))
    num = rmt_py_wrapper.intptr_value(num_ptr)
    rmt_py_wrapper.delete_intptr(num_ptr) # release num_ptr

    # Put data in JSON format
    data = {"total": num, "items": []}
    items = []
    for i in range(0, num):
        item = {
            "Index": (i+1),
            "DeviceID": str(dev_list[i].deviceID),
            "Hostname": dev_list[i].host,
            "Model": dev_list[i].model,
            "IP": dev_list[i].ip,
            "MAC": dev_list[i].mac,
            "RMT_VERSION": dev_list[i].rmt_version
        }
        items.append(item)
    data["items"] = items

    # DEBUG
    # print("=== data ===")
    # result = json.dumps(data, indent=4)
    # print(result)

    # Free dev_list
    rmt_py_wrapper.rmt_server_free_device_list(dev_list.cast())

    return data

@router.get("/discovery", response_model=schemas.Response, summary="Show current online devices")
def get_robots_list() -> Any:
    robot_data = rmt_discovery()
    return {"code": 20000, "data": robot_data}
