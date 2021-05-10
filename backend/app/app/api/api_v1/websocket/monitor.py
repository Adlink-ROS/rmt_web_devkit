from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.extensions.utils import list_to_tree
from random import randint
import rmt_py_wrapper
import json
import numpy as np
import socketio
import threading

lock = threading.Lock()

background_task_started = False
client_connecting = 0

class ServerNamespace(socketio.AsyncNamespace):

    async def on_connect(self, sid, environ):
        print(f"{sid} is connected !")
        global background_task_started, client_connecting
        lock.acquire()
        client_connecting = client_connecting + 1
        lock.release()
        if not background_task_started:
            self.server.start_background_task(self.background_task)
            background_task_started = True
        # self.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)

    async def on_disconnect(self, sid):
        print(f"{sid} is disconnected !")
        global background_task_started,client_connecting
        lock.acquire()
        client_connecting = client_connecting - 1
        lock.release()
        if client_connecting == 0:
            background_task_started = False


    async def on_disconnect_request(self, sid):
        await self.on_disconnect(sid)

    async def on_client_message(self, sid, data):
        print(data)

    async def on_my_event(self, sid, data):
        await self.emit('my_response', data)

    async def on_my_room_event(self, sid, message):
        await self.emit('my_response', {'data': message['data']}, room=message['room'])

    async def on_my_broadcast_event(self, sid, message):
        await self.emit('my_response', {'data': message['data']})

    async def on_join(self, sid, message):
        await self.enter_room(sid, message['room'])
        await self.emit('my_response', {'data': 'Entered room: ' + message['room']}, room=sid)

    async def on_leave(self, sid, message):
        await self.leave_room(sid, message['room'])
        await self.emit('my_response', {'data': 'Left room: ' + message['room']}, room=sid)

    async def on_close(self, sid, message):
        await self.emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.'}, room=message['room'])
        await self.close_room(message['room'])

    async def background_task(self):
        global background_task_started
        while background_task_started:
            sys_info = await self.hardware_info()
            await self.emit('monitor_robot', sys_info)
            await self.server.sleep(3)

    async def hardware_info(self):
        rmt_py_wrapper.rmt_server_init()

        # Get device list:
        num_ptr = rmt_py_wrapper.new_intptr()
        dev_list = rmt_py_wrapper.device_info_list.frompointer(rmt_py_wrapper.rmt_server_create_device_list(num_ptr))
        dev_num = rmt_py_wrapper.intptr_value(num_ptr)
        rmt_py_wrapper.delete_intptr(num_ptr) # release num_ptr

        # Create config key string
        config_list = ["cpu", "ram", "hostname", "wifi"]
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

        # Put data in JSON format
        data = {"total": info_num, "items": []}
        items = []
        for i in range(0, info_num):
            # Split the result string into dictionary data
            result_list = info_list[i].value_list.split(";")
            dict_data = {
                "index": (i+1),
                "deviceID": info_list[i].deviceID
            }
            for item in result_list:
                for key in config_list:
                    if key in item:
                        value = item[len(key)+1:]
                        if value.isnumeric():
                            dict_data[key] = int(value)
                        else:
                            dict_data[key] = value
            items.append(dict_data)                 

        data["items"] = items
        result = json.dumps(data, indent=4)
        print(result)

        return data
