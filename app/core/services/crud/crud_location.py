from typing import Sequence

from core.models import CoreSwitch, Location
from sqlalchemy import select

from schemas.location import LocationBase, LocationDelete, LocationUpdate
from .crud_base import BaseCRUD


class CrudLocation(BaseCRUD):

    async def create(self, schema: LocationBase) -> Location:
        stmt_name = select(Location).where(Location.name == schema.name)
        result_name = await self.session.execute(stmt_name)
        location_by_name = result_name.scalar_one_or_none()

        if location_by_name:
            raise ValueError(f"Location with name: {schema.name} already exists")

        stmt_prefix = select(Location).where(Location.prefix == schema.prefix)
        result_prefix = await self.session.execute(stmt_prefix)
        location_by_prefix = result_prefix.scalar_one_or_none()

        if location_by_prefix:
            raise ValueError(f"Location with prefix: {schema.prefix} already exists")

        location = Location(**schema.model_dump())
        self.session.add(location)
        await self.session.commit()
        await self.session.refresh(location)
        return location

    async def read(self, schema=LocationBase) -> Sequence[Location]:
        stmt = select(Location).order_by(Location.name)
        result = await self.session.scalars(stmt)
        locations = result.all()
        return locations

    async def update(self, schema: LocationUpdate, prefix=None) -> Location:
        stmt = select(Location).where(Location.prefix == prefix)
        result = await self.session.execute(stmt)
        location = result.scalar_one_or_none()

        if location is None:
            raise ValueError(f"Location {prefix} not found")

        for attr, value in schema.model_dump(exclude_none=True).items():
            setattr(location, attr, value)

        await self.session.commit()
        return location

    async def delete(self, schema: str) -> Location:
        stmt = select(Location).where(Location.prefix == schema)
        result = await self.session.execute(stmt)
        location = result.scalar_one_or_none()

        if location is None:
            raise ValueError(f"Location: {schema} не найдена")

        related_records_stmt = select(CoreSwitch).where(CoreSwitch.location_id == location.id)
        related_records_result = await self.session.execute(related_records_stmt)
        related_records = related_records_result.scalars().all()

        if related_records:
            raise ValueError(f"Невозможно удалить локацию: {schema} связано с другими записями.")

        await self.session.delete(location)
        await self.session.commit()
        return location



