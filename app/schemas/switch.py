from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .device import DeviceRead, DeviceResponse
from .validation_helper import validation_helper
from fastapi import Query


class SwitchBase(BaseModel):
    comment: Optional[str] = Field(None, max_length=50, description="Комментарий. Не более 50 символов")


class SwitchIpAddress(BaseModel):
    ip_address: Optional[str] = Field(description="IP-адрес коммутатора")

    @field_validator("ip_address")
    def validate_mac_address(cls, ip_address):
        ip_address = validation_helper.validate_ip_address(ip_address)
        return ip_address


class SwitchCreate(SwitchBase):
    ip_address: str = Field(None, description="IP-адрес коммутатора")
    snmp_oid: Optional[str] = Field("1.3.6.1.2.1.17.7.1.2.2.1.2", description="Идентификатор SNMP-агента")
    core_switch_ip: str = Field(None, description="IP-адрес опорного коммутатора")
    excluded_ports_relation: Optional[List[int]] = Field(
        [23, 24, 25, 26, 27, 28, 29, 30, 105, 209, 1000], description="Excluded ports"
    )

    @field_validator("ip_address")
    def validate_mac_address(cls, ip_address):
        ip_address = validation_helper.validate_ip_address(ip_address)
        return ip_address

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


class SwitchReadForCore(SwitchBase):
    ip_address: str
    snmp_oid: str
    excluded_ports_relation: List[SwitchExcludedPortBase] = []


class SwitchResponse(SwitchBase):
    ip_address: str
    core_switch_ip: str
    devices: Optional[List[DeviceResponse]] = []


class SwitchReadQuery(BaseModel):
    switch_comment: Optional[str] = Field(Query(
        None,
        description="Параметр поиска по полю 'comment' в таблице коммутаторов. Example: vlz"))
    ip_address: Optional[str] = Field(Query(
        None,
        description="IP-Адрес коммутатора. Example: X.X.X.X"))
    device_vlan: Optional[int] = Field(Query(
        None,
        description="Вывод устройств только с указанным VLAN. Example: 1721"))
    device_status: Optional[bool] = Field(Query(
        None,
        description="Статус доступности устройства(true - Online / false - Offline)"))
    device_comment: Optional[str] = Field(Query(
        None,
        description="Поиск по полю 'workplace_number' в таблице устройств. Example: Срёшь?"))
    device_ip_address: Optional[str] = Field(Query(
        None,
        description="IP-Адрес устройства. Example: X.X.X.X или NOT_FOUND(Если в ARP-таблице отсутствует IP-Адрес.)"))
    device_mac: Optional[str] = Field(Query(
        None,
        description="MAC-Адрес устройства. Частично или весь. Example: XX:XX или XX:XX:XX:XX:XX:XX"))
