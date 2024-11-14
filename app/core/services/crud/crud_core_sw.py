from typing import Dict, List, Sequence

from core.models import CoreSwitch, Switch
from schemas.core_switch import CoreSwitchBase, CoreSwitchCreate, CoreSwitchUpdate, CoreSwitchRead
from sqlalchemy import select
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

    async def read(self, schema=CoreSwitchRead) -> Sequence[CoreSwitch]:
        stmt = select(CoreSwitch).options(selectinload(CoreSwitch.switches)).order_by(CoreSwitch.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def update(self, schema: CoreSwitchUpdate, ip_address=None) -> CoreSwitch:
        stmt = select(CoreSwitch).where(CoreSwitch.ip_address == ip_address)
        result = await self.session.execute(stmt)
        core_switch = result.scalar_one_or_none()
        if core_switch is None:
            raise ValueError(f"Device: {ip_address} not found")
        for attr, value in schema.model_dump(exclude_none=True).items():
            setattr(core_switch, attr, value)
        await self.session.commit()
        return core_switch

    async def delete(self, schema: CoreSwitchBase) -> CoreSwitch:
        stmt = select(CoreSwitch).where(CoreSwitch.name == schema.name)
        result = await self.session.execute(stmt)
        core_switch = result.scalar_one_or_none()

        if core_switch is None:
            raise ValueError(f"Core switch: {schema.name} не найден")

        related_records_stmt = select(Switch).where(Switch.core_switch_ip == core_switch.ip_address)
        related_records_result = await self.session.execute(related_records_stmt)
        related_records = related_records_result.scalars().all()

        if related_records:
            raise ValueError(f"Невозможно удалить устройство: {schema.name} связано с другими записями.")

        await self.session.delete(core_switch)
        await self.session.commit()
        return core_switch

    async def get_snmp_params(self) -> List[Dict[str, str]]:
        """ """
        stmt = (
            select(CoreSwitch)
            .options(selectinload(CoreSwitch.switches).selectinload(Switch.excluded_ports_relation))
            .order_by(CoreSwitch.id)
        )

        result = await self.session.scalars(stmt)

        core_switches = result.all()
        formatted_result = []

        for core in core_switches:
            core_data = {"core_switch_ip": core.ip_address, "oid": core.snmp_oid, "switches": []}
            for switch in core.switches:
                switch_data = {
                    "ip_address": switch.ip_address,
                    "snmp_oid": switch.snmp_oid,
                    "excluded_ports": [
                        excluded_port.excluded_port.port_number for excluded_port in switch.excluded_ports_relation
                    ],
                }
                core_data["switches"].append(switch_data)
            formatted_result.append(core_data)

        return formatted_result
