from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.extensions.utils import list_to_tree
from random import randint
import rmt_py_wrapper
import json
import os 
import subprocess

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
            "DeviceID": dev_list[i].deviceID,
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

    # TODO: free dev_list
    # rmt_py_wrapper.rmt_server_free_device_list(dev_list)

    return data


@router.get("/discovery", response_model=schemas.Response)
def get_robots_list() -> Any:
    robot_data = rmt_discovery()
    return {"code": 20000, "data": robot_data}

def wifi_ap_init():
    result = subprocess.run(["nmcli", "con", "add", "type", "wifi", "autoconnect", "FALSE", "con-name",
                            "RMTHost", "ssid", "RMTHost"], stdout=subprocess.PIPE)
    result = subprocess.run(["nmcli", "con", "modify", "RMTHost", "802-11-wireless.mode", "ap", "802-11-wireless.band",
                            "bg", "ipv4.method", "shared"], stdout=subprocess.PIPE)
    result = subprocess.run(["nmcli", "con", "modify", "RMTHost", "802-11-wireless-security.key-mgmt", "wpa-psk"], stdout=subprocess.PIPE)

def modify_ap_config(ssid, password, band):
    result = subprocess.run(["nmcli", "con", "modify", "RMTHost", "802-11-wireless.ssid", str(ssid)], stdout=subprocess.PIPE)
    result = subprocess.run(["nmcli", "con", "modify", "RMTHost", "802-11-wireless.band", str(band)], stdout=subprocess.PIPE)
    result = subprocess.run(["nmcli", "con", "modify", "RMTHost", "802-11-wireless-security.psk", str(password)], stdout=subprocess.PIPE)
    return result

@router.post("/set_wifi_hotspot", response_model=schemas.Response)
def set_wifi_hotspot_mode(wifi_mode: schemas.WifiMode) -> Any:
    wifi_set = {"hotspot_enable": wifi_mode.hotspot_enable, "ssid": wifi_mode.ssid, "password": wifi_mode.password, "band": wifi_mode.band}
    result = subprocess.run(["nmcli", "-t", "-f", "NAME", "con", "show", "--active"], stdout=subprocess.PIPE)
    active_name = result.stdout.decode('utf-8').split("\n")
    hotspot_enable = "RMTHost" in active_name
    band_code = {"2.4 GHz": "bg", "5 GHz": "a"}
    #Create connection for the very first request
    if "RMTHost.nmconnection" not in os.listdir("/etc/NetworkManager/system-connections"):
        wifi_ap_init()
    #Exception for invalid property
    if len(wifi_set["password"]) < 8 or len(wifi_set["password"]) > 32:
        raise HTTPException(status_code=400, detail="Invalid property: Password")
    if not wifi_set["ssid"] or len(wifi_set["ssid"]) > 32:
        raise HTTPException(status_code=400, detail="Invalid property: SSID")
    if wifi_set["band"] not in band_code:
        raise HTTPException(status_code=400, detail="Invalid property: Band")

    result = modify_ap_config(wifi_set["ssid"], wifi_set["password"], band_code[wifi_set["band"]])

    if wifi_set["hotspot_enable"] != hotspot_enable:
        con_stat = "up" if wifi_set["hotspot_enable"] else "down"
        result = subprocess.run(["nmcli", "con", str(con_stat), "RMTHost"], stdout=subprocess.PIPE)

    return {"code": 20000, "data": result.stdout.decode('utf-8').rstrip("\n")}

@router.get("/get_wifi_hotspot", response_model=schemas.Response)
def get_wifi_hotspot_mode():
    if "RMTHost.nmconnection" not in os.listdir("/etc/NetworkManager/system-connections"):
        wifi_data = {
            "hotspot_enable": False,
            "ssid": "RMTserver",
            "password": "adlinkros",
            "band": "2.4 GHz"
        }

        return {"code": 20000, "data": wifi_data}

    result = subprocess.run(["nmcli", "-t", "-f", "NAME", "con", "show", "--active"], stdout=subprocess.PIPE)
    active_name = result.stdout.decode('utf-8').split("\n")
    hotspot_enable = "RMTHost" in active_name
    result = subprocess.run(["nmcli", "-f", "802-11-wireless.ssid", "connection", "show", "RMTHost"], stdout=subprocess.PIPE)
    ssid = result.stdout.decode('utf-8').replace("\n", "").split()[1]
    result = subprocess.run(["nmcli", "-s", "-f", "802-11-wireless-security.psk", "connection", "show", "RMTHost"], stdout=subprocess.PIPE)
    password = result.stdout.decode('utf-8').replace("\n", "").split()[1]
    result = subprocess.run(["nmcli","-f", "802-11-wireless.band", "connection", "show", "RMTHost"], stdout=subprocess.PIPE)
    band = result.stdout.decode('utf-8').replace("\n", "").split()[1]
    band_code = {"bg": "2.4 GHz", "a": "5 GHz"}
    band_freq = band_code[band]
    wifi_data = {
        "hotspot_enable": hotspot_enable,
        "ssid": ssid,
        "password": password,
        "band": band_freq
    }

    return {"code": 20000, "data": wifi_data}