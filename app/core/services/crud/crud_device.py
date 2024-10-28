from typing import Sequence

from core.models import Device
from schemas.device import DeviceUpdate
from sqlalchemy import select

from .crud_base import BaseCRUD


class CrudDevice(BaseCRUD):

    async def create(self, schema):
        pass

    async def read(self, schema=None) -> Sequence[Device]:
        stmt = select(Device).order_by(Device.port)
        result = await self.session.scalars(stmt)
        return result.all()

    async def update(self, schema: DeviceUpdate):
        stmt = select(Device).where(Device.mac == schema.mac)
        result = await self.session.execute(stmt)
        device = result.scalar_one_or_none()

        if device is None:
            raise ValueError(f"Device: {schema.mac} not found")

        for attr, value in schema.model_dump(exclude_none=True).items():
            setattr(device, attr, value)

        await self.session.commit()
        await self.session.refresh(device)
        return True

    async def delete(self, schema):
        pass
