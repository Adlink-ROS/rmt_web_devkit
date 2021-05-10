from typing import Optional, Any

from pydantic import BaseModel

# Shared properties
class WifiMode(BaseModel):
    hotspot_enable: bool = False
    ssid: str = "RMTserver"
    password: str = "adlinkros"
    band: str = "2.4 GHz"
