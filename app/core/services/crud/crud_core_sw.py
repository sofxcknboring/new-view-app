from typing import Sequence

from core.models import CoreSwitch
from schemas.core_switch import CoreSwitchCreate, CoreSwitchUpdate, CoreSwitchRead
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .crud_base import BaseCRUD


class CrudCoreSwitch(BaseCRUD):

    async def create(self, schema: CoreSwitchCreate) -> CoreSwitch:
        core_switch = CoreSwitch(**schema.model_dump())
        self.session.add(core_switch)
        await self.session.commit()
        await self.session.refresh(core_switch)
        return core_switch

    async def read(self, schema=None) -> Sequence[CoreSwitch]:
        stmt = select(CoreSwitch).options(selectinload(CoreSwitch.switches)).order_by(CoreSwitch.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def update(self, core_switch_ip, schema: CoreSwitchUpdate) -> CoreSwitch:
        stmt = select(CoreSwitch).where(CoreSwitch.ip_address == core_switch_ip)
        result = await self.session.execute(stmt)
        core_switch = result.scalar_one_or_none()

        if core_switch is None:
            raise ValueError(f"Core switch: {core_switch_ip} not found")

        for attr, value in schema.model_dump(exclude_none=True).items():
            setattr(core_switch, attr, value)

        await self.session.commit()
        await self.session.refresh(core_switch)
        return core_switch

    async def delete(self, core_switch_ip) -> bool:
        stmt = select(CoreSwitch).where(CoreSwitch.ip_address == core_switch_ip)
        result = await self.session.execute(stmt)
        core_switch = result.scalar_one_or_none()

        if core_switch is None:
            return False

        await self.session.delete(core_switch)
        await self.session.commit()
        return True
