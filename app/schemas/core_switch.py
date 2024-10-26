from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from schemas.switch import SwitchBase

from .validation_helper import validation_helper


class CoreSwitchBase(BaseModel):
    name: Optional[str] = Field(None, max_length=50, description="Коммент. Не более 50 символов")


class CoreSwitchCreate(CoreSwitchBase):
    ip_address: Optional[str] = Field(None, description="IP-адрес опорного коммутатора")
    snmp_oid: Optional[str] = Field("1.3.6.1.2.1.4.22.1.2", description="Идентификатор SNMP-агента")

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, value: Optional[str]) -> Optional[str]:
        return validation_helper.validate_ip_address(ip=value)


class CoreSwitchUpdate(CoreSwitchCreate):
    pass


class CoreSwitchRead(CoreSwitchBase):
    id: int
    ip_address: str
    snmp_oid: str
    switches: Optional[List[SwitchBase]] = []
