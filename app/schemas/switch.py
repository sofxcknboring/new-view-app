from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .device import DeviceRead, DeviceResponse
from .validation_helper import validation_helper


class SwitchBase(BaseModel):
    comment: Optional[str] = Field(None, max_length=50, description="Комментарий. Не более 50 символов")


class SwitchIpAddress(BaseModel):
    ip_address: Optional[str] = Field(description="IP-адрес коммутатора")

    @field_validator("ip_address")
    def validate_mac_address(cls, ip_address):
        ip_address = validation_helper.validate_ip_address(ip_address)
        return ip_address


class SwitchCreate(SwitchBase):
    ip_address: SwitchIpAddress = Field(None, description="IP-адрес коммутатора")
    snmp_oid: Optional[str] = Field("1.3.6.1.2.1.17.7.1.2.2.1.2", description="Идентификатор SNMP-агента")
    core_switch_ip: str = Field(None, description="IP-адрес опорного коммутатора")
    excluded_ports_relation: Optional[List[int]] = Field(
        [23, 24, 25, 26, 27, 28, 29, 30, 105, 209, 1000], description="Excluded ports"
    )


class SwitchUpdate(SwitchCreate):
    pass


class ExcludedPortBase(BaseModel):
    id: int
    port_number: int
    comment: Optional[str] = None


class SwitchExcludedPortBase(BaseModel):
    switch_id: int
    excluded_port: ExcludedPortBase


class SwitchRead(SwitchBase):
    id: int
    ip_address: SwitchIpAddress
    snmp_oid: str
    core_switch_ip: str
    devices: Optional[List[DeviceRead]] = []
    excluded_ports_relation: List[SwitchExcludedPortBase] = []


class SwitchResponse(SwitchBase):
    ip_address: str
    core_switch_ip: str
    devices: Optional[List[DeviceResponse]] = []
