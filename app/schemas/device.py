from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DeviceBase(BaseModel):
    workplace_number: Optional[str] = Field(None, max_length=50, description="Комментарий, не более 50 символов")


class DeviceCreate(DeviceBase):
    switch: str = Field(..., alias="SWITCH")
    vlan: int = Field(..., alias="VLAN")
    mac: str = Field(..., alias="MAC")
    port: int = Field(..., alias="PORT")
    ip: str = Field(..., alias="IP")


class DeviceDataList(BaseModel):
    devices: List[DeviceCreate]


class DeviceUpdate(DeviceBase):
    ip: str


class DeviceRead(DeviceBase):
    id: int
    port: int
    mac: str
    vlan: int
    ip_address: str
    status: bool
    update_time: datetime
    switch_id: int


class DeviceResponse(DeviceBase):
    ip_address: str
    mac: str
    port: int
    vlan: int
    status: bool
    update_time: datetime
