from typing import Optional

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    name: str
    prefix: str

    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None)
    prefix: Optional[str] = Field(None)

    class Config:
        from_attributes = True

class LocationDelete(BaseModel):
    name: str

    class Config:
        from_attributes = True

