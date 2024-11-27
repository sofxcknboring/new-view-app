from pydantic import BaseModel


class VlanBase(BaseModel):
    id: int
    vlan: int

    class Config:
        from_attributes = True
