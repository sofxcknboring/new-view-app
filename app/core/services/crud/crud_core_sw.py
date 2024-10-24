from typing import Sequence

from core.models import CoreSwitch, db_helper
from fastapi import Depends
from schemas.core_switch import CoreSwitchCreate, CoreSwitchUpdate, CoreSwitchBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .crud_base import BaseCRUD


class CrudCoreSwitch(BaseCRUD):
    """
    Crud класс для опорных коммутаторов.
    """

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

    async def update(self, schema: CoreSwitchUpdate) -> CoreSwitch:
        stmt = select(CoreSwitch).where(CoreSwitch.ip_address == schema.ip_address)
        result = await self.session.execute(stmt)
        core_switch = result.scalar_one_or_none()

        if core_switch is None:
            raise ValueError(f"Core switch: {schema.ip_address} not found")

        for attr, value in schema.model_dump(exclude_none=True).items():
            setattr(core_switch, attr, value)

        await self.session.commit()
        await self.session.refresh(core_switch)
        return core_switch

    async def delete(self, schema: CoreSwitchBase) -> bool:
        stmt = select(CoreSwitch).where(CoreSwitch.name == schema.name)
        result = await self.session.execute(stmt)
        core_switch = result.scalar_one_or_none()

        if core_switch is None:
            return False

        await self.session.delete(core_switch)
        await self.session.commit()
        return True


def get_crud_core_switch(session: AsyncSession = Depends(db_helper.session_getter)) -> CrudCoreSwitch:
    """
    Получает экземпляр класса CrudCoreSwitch с использованием асинхронной сессии базы данных.

    Эта функция используется в качестве зависимости в маршрутах FastAPI для предоставления
    экземпляра CrudCoreSwitch, который может быть использован для выполнения CRUD-операций
    с объектами CoreSwitch.

    Args:
        session (AsyncSession, optional): Асинхронная сессия базы данных, полученная через
            зависимость db_helper.session_getter. По умолчанию None.

    Returns:
        CrudCoreSwitch: Экземпляр класса CrudCoreSwitch, готовый к использованию для
        выполнения операций с базой данных.
    """
    return CrudCoreSwitch(session=session)
