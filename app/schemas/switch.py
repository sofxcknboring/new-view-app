from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .device import DeviceResponse
from .validation_helper import validation_helper
from fastapi import Query


class SwitchBase(BaseModel):
    comment: Optional[str] = Field(None, max_length=50)

    class Config:
        from_attributes = True


class SwitchIpAddress(BaseModel):
    ip_address: Optional[str] = Field(None)

    @field_validator("ip_address")
    def validate_mac_address(cls, ip_address):
        ip_address = validation_helper.validate_ip_address(ip_address)
        return ip_address


class SwitchCreate(SwitchBase):
    ip_address: str = Field(None)
    snmp_oid: Optional[str] = Field("1.3.6.1.2.1.17.7.1.2.2.1.2")
    core_switch_ip: str = Field(None)
    excluded_ports_relation: Optional[List[int]] = Field([23, 24, 25, 26, 27, 28, 29, 30, 105, 209, 1000])

    @field_validator("ip_address", "core_switch_ip")
    def validate_ip_address(cls, ip_address):
        ip_address = validation_helper.validate_ip_address(ip_address)
        return ip_address

    @field_validator("snmp_oid")
    def validate_snmp_oid(cls, oid):
        if oid is None:
            return "1.3.6.1.2.1.17.7.1.2.2.1.2"
        return validation_helper.validate_switch_oid(oid=oid)


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
    ip_address: str
    snmp_oid: str
    core_switch_ip: str
    excluded_ports: List[int]


class SwitchReadForCore(SwitchBase):
    ip_address: str
    snmp_oid: str


class SwitchResponse(SwitchBase):
    ip_address: str
    core_switch_ip: str
    devices: Optional[List[DeviceResponse]] = []


class SwitchReadQuery(BaseModel):
    switch_comment: Optional[str] = Field(Query(None))
    ip_address: Optional[str] = Field(Query(None))
    device_vlan: Optional[int] = Field(Query(None))
    device_status: Optional[bool] = Field(Query(None))
    device_comment: Optional[str] = Field(Query(None))
    device_ip_address: Optional[str] = Field(Query(None))
    device_mac: Optional[str] = Field(Query(None))
