
from posix import listdir
from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import Any
from starlette.responses import StreamingResponse
from app import schemas
import io
import os
import rmt_py_wrapper
import json
import time

router = APIRouter()
UPLOAD_PATH = "/tmp/rmt/"

@router.get("/file_upload_list", response_model=schemas.Response, summary="List all the uploaded files on the host server")
def file_upload_list() -> Any:
    code = 20000
    data = {}
    msg = ""

    # create dir if not exist
    if not os.path.exists(UPLOAD_PATH):
        os.makedirs(UPLOAD_PATH)

    # list all the files in UPLOAD_PATH
    file_list = listdir(UPLOAD_PATH)

    # put file_list into JSON data
    data["file_upload_list"] = file_list

    return {"code": code, "data": data, "message": msg}

@router.post("/file_upload_remove", response_model=schemas.Response, summary="Delete the uploaded file from the host server")
def file_upload_remove(file_req_body: schemas.RemoveFile_ReqBody) -> Any:
    code = 40400 # not found for default
    data = {}
    msg = ""

    filename = file_req_body.filename
    filepath = UPLOAD_PATH + filename
    try:
        # remove the target file from disk
        os.remove(filepath)
    except Exception as e:
        code = 40000
        msg = str(e)
    else:
        code = 20000
        data = {
            "filename": filename,
            "status": 0
        }
        
    return {"code": code, "data": data, "message": msg}

@router.post("/file_upload_add", response_model=schemas.Response, summary="Upload the file to the host server")
def file_upload_add(myfile: UploadFile = File(...)) -> Any:
    code = 40400 # not found for default
    data = {}
    msg = ""

    filename = myfile.filename
    filepath = UPLOAD_PATH + filename
    content = myfile.file.read()

    # DEBUG:
    # print("filename={}".format(filename))
    # print("content={}".format(content))

    try:
        # create dir if not exist
        if not os.path.exists(UPLOAD_PATH):
            os.makedirs(UPLOAD_PATH)        
        # create file in binary mode
        f = open(filepath, "wb")
    except OSError as e:
        msg = str(e)
        code = 40300
    else:
        # write file to disk
        f.write(content)
        f.close()
        data = {
            "filename": filename,
            "content_type": myfile.content_type
        }
        code = 20000

    return {"code": code, "data": data, "message": msg}

@router.post("/file_upload_send_check", response_model=schemas.Response, summary="Check the result of file transfering")
def file_upload_send_check(file_req_body: schemas.SendFileCheck_ReqBody) -> Any:
    code = 40400 # not found for default
    data = {}
    msg = ""

    dev_num = len(file_req_body.device_list)
    for i in range(0, dev_num):
        device_dict = {}
        device_id = int(file_req_body.device_list[i])

        # check the transmission result for the previous send
        status, result, byte_array = rmt_py_wrapper.rmt_server_get_result(device_id)        
        device_dict["status"] = status
        device_dict["result"] = result
        data[device_id] = device_dict
        code = 20000
        # TODO: status & result checking

    # DEBUG msg
    # json_debug = json.dumps(data, indent=4)
    # print(json_debug)

    return {"code": code, "data": data, "message": msg}

@router.post("/file_upload_send", response_model=schemas.Response, summary="Choose one of the uploaded files to be sent from the host server to the target devices")
def file_upload_send(file_req_body: schemas.UploadFileById_ReqBody) -> Any:
    code = 20000
    data = {}
    msg = ""

    callback = file_req_body.callback
    filename = file_req_body.filename
    filepath = UPLOAD_PATH + filename

    try:
        # open the uploaded file
        f = open(filepath, "rb")
    except OSError as e:
        msg = str(e)
        code = 40400
    else:
        # read the file content to memory
        content = f.read()
        f.close()

        # DEBUG:
        # print("filename={}".format(filename))
        # print("content={}".format(content))

        dev_num = len(file_req_body.device_list)
        id_list = rmt_py_wrapper.ulong_array(dev_num)
        for i in range(0, dev_num):
            id_list[i] = int(file_req_body.device_list[i])

        # send the file content to the target device
        status = rmt_py_wrapper.rmt_server_send_file(id_list, dev_num, callback, filename, content)
        code = 20000
        data = {
            "filename" : filename,
            "status" : status
        }

    return {"code": code, "data": data, "message": msg}

@router.post("/file_download", response_model=schemas.Response, summary="Directly download a file from the target device")
def file_download(file_req_body: schemas.DownloadFileById_ReqBody) -> Any:
    device_id = int(file_req_body.device_id)
    callback = file_req_body.callback
    filename = file_req_body.filename
 
    # ask agent start to transfer the file
    agent_status = rmt_py_wrapper.rmt_server_recv_file(device_id, callback, filename)

    # get the result for file transmission 
    agent_status, result, byte_array = rmt_py_wrapper.rmt_server_get_result(device_id)

    # keep checking result while ther transmission is still running
    while agent_status == rmt_py_wrapper.STATUS_RUNNING:
        time.sleep(1) # wait for 1 second to check
        agent_status, result, byte_array = rmt_py_wrapper.rmt_server_get_result(device_id)

    # DEBUG:
    # print("device_id={}".format(device_id))
    # print("filename={}".format(filename))
    # print("agent_status=%d" % agent_status)
    # print("transfer_result=%d" % result)
    # print("file_len=%d" % len(byte_array))
    # print("=== file content start ===")
    # print(bytes(byte_array).decode("utf-8"))
    # print("\n=== file content end ===")

    # return file for user to download
    return StreamingResponse(
        io.BytesIO(bytes(byte_array)), 
        media_type="application/octet-stream", 
        headers={
            "Content-Disposition": "attachment;filename="+filename
        }
    )
