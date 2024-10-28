from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DeviceBase(BaseModel):
    workplace_number: Optional[str] = Field(None, max_length=50, description="Комментарий, не более 50 символов")


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(DeviceBase):
    mac: str

class DeviceRead(DeviceBase):
    id: int
    port: int
    mac: str
    vlan: int
    ip_address: str
    status: bool
    update_time: datetime
    switch_id: int

