from typing import Any, Optional

from fastapi import APIRouter, HTTPException, File, UploadFile
from app import schemas
import rmt_py_wrapper
import json
import os 
import subprocess

router = APIRouter()

@router.post("/file_transfer", response_model=schemas.Response)
def file_transfer(myfile: UploadFile = File(...)) -> Any:
    code = 40400 # not found for default
    content = myfile.file.read()
    print("content=")
    print(content)
    data = {
        "filename": myfile.filename,
        "content_type": myfile.content_type
    }
    if data:
        # found => 200 OK
        code = 20000

    return {"code": code, "data": data}
