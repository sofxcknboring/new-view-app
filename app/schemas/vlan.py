from pydantic import BaseModel


class VlanBase(BaseModel):
    id: int
    vlan: int

    class Config:
        orm_mode = True

