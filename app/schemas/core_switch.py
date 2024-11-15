from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from schemas.switch import SwitchReadForCore

from .validation_helper import validation_helper


class CoreSwitchBase(BaseModel):
    comment: Optional[str] = Field(None, max_length=50)

    class Config:
        from_attributes = True


class CoreSwitchCreate(CoreSwitchBase):
    prefix: str
    ip_address: Optional[str] = Field(None)
    snmp_oid: Optional[str] = Field("1.3.6.1.2.1.4.22.1.2")

    @field_validator("ip_address")
    def validate_ip_address(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            return validation_helper.validate_ip_address(ip=value)
        return value

    @field_validator("snmp_oid")
    def validate_snmp_oid(cls, value: Optional[str]) -> str:
        if value is None:
            return "1.3.6.1.2.1.4.22.1.2"
        return validation_helper.validate_core_switch_oid(oid=value)


class CoreSwitchUpdate(CoreSwitchCreate):
    pass


class CoreSwitchResponse(CoreSwitchBase):
    id: int
    ip_address: str
    snmp_oid: str


class CoreSwitchRead(CoreSwitchBase):
    location_name: str
    ip_address: str
    snmp_oid: str
    switches: Optional[List[SwitchReadForCore]] = []


class CoreSwitchDelete(BaseModel):
    ip_address: str
