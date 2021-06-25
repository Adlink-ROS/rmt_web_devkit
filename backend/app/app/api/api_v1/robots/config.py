from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.extensions.utils import list_to_tree
from random import randint
import rmt_py_wrapper
import json
import os 
import subprocess
import re

router = APIRouter()

def rmt_get_config_for_all(dev_list, dev_num, config_list):
    # Create config key string
    config_key_str = ""
    for item in config_list:
        config_key_str += item + ';'

    # Get device info list
    id_list = rmt_py_wrapper.ulong_array(dev_num)
    for i in range(0, dev_num):
        id_list[i] = dev_list[i].deviceID
    info_num_ptr = rmt_py_wrapper.new_intptr()
    info_list = rmt_py_wrapper.data_info_list.frompointer(rmt_py_wrapper.rmt_server_get_info(id_list, dev_num, config_key_str, info_num_ptr))
    info_num = rmt_py_wrapper.intptr_value(info_num_ptr)
    rmt_py_wrapper.delete_intptr(info_num_ptr) # release info_num_ptr
    
    # print("=== get config result ===")
    config_data = {}
    for i in range(0, info_num):
        # Split the result string into dictionary data
        result_list = info_list[i].value_list.split(";")
        device_dict = {}
        device_id = info_list[i].deviceID
        for item in result_list:
            for key in config_list:
                if key == item[0:len(key)]:
                    device_dict[key] = item[len(key)+1:]
        # print(device_dict)
        config_data[device_id] = device_dict
    # result = json.dumps(config_data, indent=4)
    # print(result)

    return config_data

def rmt_get_same_config_by_id(target_list, target_num, config_list):
    # Create config key string
    config_key_str = ""
    for item in config_list:
        config_key_str += item + ';'

    # Get device info list
    id_list = rmt_py_wrapper.ulong_array(target_num)
    for i in range(0, target_num):
        id_list[i] = int(target_list[i])
    info_num_ptr = rmt_py_wrapper.new_intptr()
    info_list = rmt_py_wrapper.data_info_list.frompointer(rmt_py_wrapper.rmt_server_get_info(id_list, target_num, config_key_str, info_num_ptr))
    info_num = rmt_py_wrapper.intptr_value(info_num_ptr)
    rmt_py_wrapper.delete_intptr(info_num_ptr) # release info_num_ptr
    
    config_data = {}
    for i in range(0, info_num):
        # Split the result string into dictionary data
        result_list = info_list[i].value_list.split(";")
        device_dict = {}
        device_id = info_list[i].deviceID
        for item in result_list:
            for key in config_list:
                if key == item[0:len(key)]:
                    device_dict[key] = item[len(key)+1:]
        # print(device_dict)
        config_data[device_id] = device_dict
    # result = json.dumps(config_data, indent=4)
    # print(result)

    return config_data

def rmt_set_same_config_by_id(target_list, target_num, config_dict):
    # Convert config_dict to config_str
    config_str = ""
    for key, value in config_dict.items():
        config_str += key + ':' + value + ';'

    # Convert target_list to id_list
    id_list = rmt_py_wrapper.ulong_array(target_num)
    for i in range (0, target_num):
        id_list[i] = int(target_list[i])

    # Send id_list and config_str to RMT library
    info_num_ptr = rmt_py_wrapper.new_intptr()
    info_list = rmt_py_wrapper.data_info_list.frompointer(rmt_py_wrapper.rmt_server_set_info_with_same_value(id_list, target_num, config_str, info_num_ptr))
    info_num = rmt_py_wrapper.intptr_value(info_num_ptr)
    rmt_py_wrapper.delete_intptr(info_num_ptr) # release info_num_ptr

    # print("=== set same config result ===")
    config_data = {}
    for i in range(0, info_num):
        # Split the result string into dictionary data
        result_list = info_list[i].value_list.split(";")
        device_dict = {}
        device_id = info_list[i].deviceID
        for item in result_list:
            key_value_pair = item.split(":")
            if len(key_value_pair) > 1:
                key = key_value_pair[0]
                value = key_value_pair[1]
                device_dict[key] = value
        config_data[device_id] = device_dict

    # DEBUG 
    # result = json.dumps(config_data, indent=4)
    # print(result)

    return config_data

def rmt_set_diff_config_by_id(device_config_json):
    # Create data_info_array to save configurations for each device
    target_num = len(device_config_json.keys())
    data_info_array = rmt_py_wrapper.new_data_info_array(target_num)
    idx = 0
    for deviceID, config in device_config_json.items():
        # Convert config to config_str
        config_str = ""
        for key, value in config.items():
            config_str += key + ':' + value + ';'
        # Save config data to data_info_array
        data_info_element = rmt_py_wrapper.data_info()
        data_info_element.deviceID = int(deviceID)
        data_info_element.value_list = config_str
        rmt_py_wrapper.data_info_array_setitem(data_info_array, idx, data_info_element)
        idx += 1

    # DEBUG: Print what we want to set in data_info_array
    # print("=== set diff config req ===")
    # for i in range (0, target_num):
    #     data_info_element = rmt_py_wrapper.data_info_array_getitem(data_info_array, i)
        # print("deviceID=%d" % data_info_element.deviceID)
        # print("value_list=%s" % data_info_element.value_list)

    # Send data_info_array to RMT library
    info_num_ptr = rmt_py_wrapper.new_intptr()
    info_list = rmt_py_wrapper.data_info_list.frompointer(rmt_py_wrapper.rmt_server_set_info(data_info_array, target_num, info_num_ptr))
    info_num = rmt_py_wrapper.intptr_value(info_num_ptr)
    rmt_py_wrapper.delete_intptr(info_num_ptr) # release info_num_ptr

    # print("=== set diff config result ===")
    config_data = {}
    for i in range(0, info_num):
        # Split the result string into dictionary data
        result_list = info_list[i].value_list.split(";")
        device_dict = {}
        device_id = info_list[i].deviceID
        for item in result_list:
            key_value_pair = item.split(":")
            if len(key_value_pair) > 1:
                key = key_value_pair[0]
                value = key_value_pair[1]
                device_dict[key] = value
        config_data[device_id] = device_dict
        
    # DEBUG 
    # result = json.dumps(config_data, indent=4)
    # print(result)

    return config_data

def rmt_set_seq_config_by_id(device_list, config_dict):
    # Create data_info_array to save configurations for each device
    target_num = len(device_list)
    data_info_array = rmt_py_wrapper.new_data_info_array(target_num)

    for i in range(0, target_num):
        config_str = ""
        # Increment config value for each loop
        for key, value in config_dict.items():
            if i > 0:
                new_value = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}", 
                    value)
                value = new_value
            config_str += key + ':' + value + ';'

        # Save config data to data_info_array
        data_info_element = rmt_py_wrapper.data_info()
        data_info_element.deviceID = int(device_list[i])
        data_info_element.value_list = config_str
        rmt_py_wrapper.data_info_array_setitem(data_info_array, i, data_info_element)

    # DEBUG: Print what we want to set in data_info_array
    # print("=== set sequential config req ===")
    # for i in range(0, target_num):
    #     data_info_element = rmt_py_wrapper.data_info_array_getitem(data_info_array, i)
    #     print("deviceID=%d" % data_info_element.deviceID)
    #     print("value_list=%s" % data_info_element.value_list)

    # Send data_info_array to RMT library
    info_num_ptr = rmt_py_wrapper.new_intptr()
    info_list = rmt_py_wrapper.data_info_list.frompointer(rmt_py_wrapper.rmt_server_set_info(data_info_array, target_num, info_num_ptr))
    info_num = rmt_py_wrapper.intptr_value(info_num_ptr)
    rmt_py_wrapper.delete_intptr(info_num_ptr) # release info_num_ptr

    # print("=== set sequential config result ===")
    config_data = {}
    for i in range(0, info_num):
        # Split the result string into dictionary data
        result_list = info_list[i].value_list.split(";")
        device_dict = {}
        device_id = info_list[i].deviceID
        for item in result_list:
            key_value_pair = item.split(":")
            if len(key_value_pair) > 1:
                key = key_value_pair[0]
                value = key_value_pair[1]
                device_dict[key] = value
        config_data[device_id] = device_dict

    # DEBUG 
    # result = json.dumps(config_data, indent=4)
    # print(result)

    return config_data

def rmt_discovery():
    num_ptr = rmt_py_wrapper.new_intptr()
    dev_list = rmt_py_wrapper.device_info_list.frompointer(rmt_py_wrapper.rmt_server_create_device_list(num_ptr))
    num = rmt_py_wrapper.intptr_value(num_ptr)
    rmt_py_wrapper.delete_intptr(num_ptr) # release num_ptr
    return dev_list, num

@router.post("/get_config_for_all", response_model=schemas.Response, summary="Get the config settings of all the devices")
def get_config_for_all(config_req_body: schemas.GetConfigForAll_ReqBody) -> Any:
    code = 40400 # not found for default
    dev_list, num = rmt_discovery()
    data = rmt_get_config_for_all(dev_list, num, config_req_body.config_list)
    if data:
        # found => 200 OK
        code = 20000
    # TODO: free dev_list
    # rmt_py_wrapper.rmt_server_free_device_list(dev_list)
    return {"code": code, "data": data}

@router.post("/get_same_config_by_id", response_model=schemas.Response, summary="Get the config settings of input devices")
def get_same_config_by_id(config_req_body: schemas.GetSameConfigById_ReqBody) -> Any:
    code = 40400 # not found for default
    target_list = config_req_body.device_list
    config_list = config_req_body.config_list
    target_num = len(target_list)
    data = rmt_get_same_config_by_id(target_list, target_num, config_list)
    if data:
        # found => 200 OK
        code = 20000
    # print(data)
    # TODO: free dev_list
    # rmt_py_wrapper.rmt_server_free_device_list(dev_list)
    return {"code": code, "data": data}

# @router.post("/get_diff_config_by_id", response_model=schemas.Response)
# def get_diff_config_by_id(config_req_body: GetDiffConfigById_ReqBody) -> Any:
#     pass

@router.put("/set_same_config_by_id", response_model=schemas.Response, summary="Configure the input settings to the target devices")
def set_same_config_by_id(config_req_body: schemas.SetSameConfigById_ReqBody) -> Any:
    code = 40400 # not found for default
    target_list = config_req_body.device_list
    config_dict = config_req_body.config_dict
    target_num = len(target_list)
    data = rmt_set_same_config_by_id(target_list, target_num, config_dict)
    if data:
        # found => 200 OK
        code = 20000
    return {"code": code, "data": data}

@router.put("/set_diff_config_by_id", response_model=schemas.Response, summary="Customize settings for each devices")
def set_diff_config_by_id(config_req_body: schemas.SetDiffConfigById_ReqBody) -> Any:
    code = 40400 # not found for default
    data = rmt_set_diff_config_by_id(config_req_body.device_config_json)
    if data:
        # found => 200 OK
        code = 20000
    return {"code": code, "data": data}

@router.put("/set_sequential_config_by_id", response_model=schemas.Response, summary="Configure sequential numbering settings for the target devices")
def set_seq_config_by_id(config_req_body: schemas.SetSequentialConfigById_ReqBody) -> Any:
    code = 40400 # not found for default
    device_list = config_req_body.device_list
    config_dict = config_req_body.numbering_config_start
    data = rmt_set_seq_config_by_id(device_list, config_dict)
    if data:
        # found => 200 OK
        code = 20000
    return {"code": code, "data": data}