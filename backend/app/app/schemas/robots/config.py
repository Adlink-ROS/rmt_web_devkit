from typing import Optional, Any
from typing import List, Dict
from pydantic import BaseModel

class SetSameConfigById_ReqBody(BaseModel):
    device_list: List[str] = ["5566", "6166"]
    config_dict: Dict[str, str] = {
        "locate": "on"
    }

class SetDiffConfigById_ReqBody(BaseModel):
    device_config_json: Dict[str, dict] = {
        "5566": {
            "hostname": "ROScube-1",
            "locate": "on"
        },
        "6166": {
            "hostname": "ROScube-2",
            "locate": "on"            
        }
    }

class SetSequentialConfigById_ReqBody(BaseModel):
    device_list: List[str] = ["5566", "5567", "5568", "5569"]
    numbering_config_start: Dict[str, str] = {
        "ip": "192.168.0.1",
        "hostname": "roscube1"
    }

class GetSameConfigById_ReqBody(BaseModel):
    device_list: List[str] = ["5566", "6166"]
    config_list: List[str] = ["cpu", "ram", "hostname", "wifi"]

class GetConfigForAll_ReqBody(BaseModel):
    config_list: List[str] = ["cpu", "ram", "hostname", "wifi"]