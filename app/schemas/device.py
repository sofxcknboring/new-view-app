from datetime import datetime
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, Field


class DeviceBase(BaseModel):
    workplace_number: Optional[str] = Field(None, max_length=50)

    class Config:
        from_attributes = True


class DeviceCreate(BaseModel):
    vlan: int = Field(..., alias="VLAN")
    mac: str = Field(..., alias="MAC")
    port: int = Field(..., alias="PORT")
    ip: str = Field(..., alias="IP")


class SwitchDevices(BaseModel):
    switch: str = Field(..., alias="SWITCH")
    devices: List[DeviceCreate]


class DevicesSnmpResponse(BaseModel):
    switches: List[SwitchDevices]


class DeviceUpdate(DeviceBase):
    pass


class DeviceRead(DeviceBase):
    id: int
    port: int
    mac: str
    vlan: int
    ip_address: str
    status: bool
    update_time: datetime
    switch_id: int


class DeviceQuery(BaseModel):
    ip_address: Optional[str] = Field(Query(None))


class DeviceResponse(DeviceBase):
    ip_address: str
    mac: str
    port: int
    vlan: int
    status: bool
    update_time: datetime
