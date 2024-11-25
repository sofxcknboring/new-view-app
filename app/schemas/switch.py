from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .device import DeviceResponse
from .validation_helper import validation_helper
from fastapi import Query


class SwitchBase(BaseModel):

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
    core_switch_ip: str = Field(None)

    @field_validator("ip_address", "core_switch_ip")
    def validate_ip_address(cls, ip_address):
        ip_address = validation_helper.validate_ip_address(ip_address)
        return ip_address


class SwitchUpdate(SwitchCreate):
    snmp_oid: Optional[str] = Field('1.3.6.1.2.1.17.7.1.2.2.1.2')
    comment: Optional[str] = Field(None, max_length=100)
    @field_validator("snmp_oid")
    def validate_snmp_oid(cls, oid):
        if oid is None:
            return "1.3.6.1.2.1.17.7.1.2.2.1.2"
        return validation_helper.validate_switch_oid(oid=oid)


class PortBase(BaseModel):
    id: int
    port_number: int
    comment: Optional[str] = None


class SwitchPortBase(BaseModel):
    switch_id: int
    port: PortBase


class SwitchRead(SwitchBase):
    ip_address: str
    snmp_oid: str
    core_switch_ip: str
    comment: Optional[str] = Field(None, max_length=100)
    ports: List[int]


class SwitchConfRead(SwitchBase):
    ip_address: str
    location_name: str
    snmp_oid: str
    core_switch_ip: str
    comment: Optional[str] = Field(None, max_length=100)
    ports: List[int]
    devices_count: int


class SwitchReadForCore(SwitchBase):
    ip_address: str
    snmp_oid: str
    comment: Optional[str] = Field(None, max_length=100)


class SwitchResponse(SwitchBase):
    ip_address: str
    core_switch_ip: str
    comment: Optional[str] = Field(None, max_length=100)
    devices: Optional[List[DeviceResponse]] = []


class SwitchReadQuery(BaseModel):
    switch_comment: Optional[str] = Field(Query(None))
    ip_address: Optional[str] = Field(Query(None))
    device_vlan: Optional[int] = Field(Query(None))
    device_status: Optional[bool] = Field(Query(None))
    device_comment: Optional[str] = Field(Query(None))
    device_ip_address: Optional[str] = Field(Query(None))
    device_mac: Optional[str] = Field(Query(None))
