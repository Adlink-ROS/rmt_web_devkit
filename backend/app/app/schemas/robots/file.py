from typing import Optional, Any
from typing import List, Dict
from pydantic import BaseModel

class DownloadFileById_ReqBody(BaseModel):
    device_id: str = "6166"
    callback: str = "custom_callback"
    filename: str = "testfile"

class UploadFileById_ReqBody(BaseModel):
    device_list: List[str] = ["5566", "6166"]
    callback: str = "custom_callback"
    filename: str = "testfile"

class SendFileCheck_ReqBody(BaseModel):
    device_list: List[str] = ["5566", "6166"]

class RemoveFile_ReqBody(BaseModel):
    filename: str = "testfile"
