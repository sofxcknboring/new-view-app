from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .device import DeviceRead
from .validation_helper import validation_helper


class SwitchBase(BaseModel):
    comment: Optional[str] = Field(None, max_length=50, description="Комментарий. Не более 50 символов")


class SwitchCreate(SwitchBase):
    ip_address: Optional[str] = Field(None, description="IP-адрес коммутатора")
    snmp_oid: Optional[str] = Field("1.3.6.1.2.1.17.7.1.2.2.1.2", description="Идентификатор SNMP-агента")
    core_switch_ip: str = Field(None, description="IP-адрес опорного коммутатора")
    excluded_ports_relation: Optional[List[int]] = Field(None, description="Excluded ports")

    @field_validator("ip_address", "core_switch_ip")
    @classmethod
    def validate_ip_address(cls, value: Optional[str]) -> Optional[str]:
        return validation_helper.validate_ip_address(ip=value)


class SwitchUpdate(SwitchCreate):
    pass


class SwitchIpAddress(BaseModel):
    ip_address: Optional[str] = Field(description="IP-адрес коммутатора")

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, value: Optional[str]) -> Optional[str]:
        return validation_helper.validate_ip_address(ip=value)


class ExcludedPortBase(BaseModel):
    id: int
    port_number: int
    comment: Optional[str] = None


class SwitchExcludedPortBase(BaseModel):
    switch_id: int
    excluded_port: ExcludedPortBase


class SwitchRead(SwitchBase):
    id: int
    ip_address: str
    snmp_oid: str
    core_switch_ip: str
    devices: Optional[List[DeviceRead]] = []
    excluded_ports_relation: List[SwitchExcludedPortBase] = []
