from typing import Dict, List
from core.models import CoreSwitch, Location, Switch
from schemas.core_switch import CoreSwitchCreate, CoreSwitchDelete, CoreSwitchRead, CoreSwitchUpdate
from schemas.switch import SwitchReadForCore
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..snmp import SnmpV3
from ..snmp.snmp_formatters import CoreSwitchFormatter
from .crud_base import BaseCRUD


class CrudCoreSwitch(BaseCRUD):
    """
    Crud класс для опорных коммутаторов.
    """

    async def create(self, schema: CoreSwitchCreate) -> CoreSwitch:
        try:
            core_switch_walker = SnmpV3(format_class=CoreSwitchFormatter)
            core_switch_name = await core_switch_walker.get_sys_descr(schema.ip_address)
        except Exception:
            raise
        else:
            stmt = select(Location).where(Location.prefix == schema.prefix)
            result = await self.session.execute(stmt)
            location = result.scalar_one_or_none()
            if not location:
                raise ValueError("Location with this name does not exist.")

            core_switch = CoreSwitch(
                **schema.model_dump(exclude={"prefix"}), location_id=location.id, comment=core_switch_name
            )
            self.session.add(core_switch)
            await self.session.commit()
            await self.session.refresh(core_switch)
            return core_switch

    async def read(self, schema=CoreSwitchRead) -> List[CoreSwitchRead]:
        stmt = (
            select(CoreSwitch)
            .options(selectinload(CoreSwitch.location), selectinload(CoreSwitch.switches))
            .order_by(CoreSwitch.id)
        )
        result = await self.session.scalars(stmt)
        core_switches = result.all()

        return [
            CoreSwitchRead(
                id=switch.id,
                comment=switch.comment,
                ip_address=switch.ip_address,
                snmp_oid=switch.snmp_oid,
                location_name=switch.location.name,
                location_prefix=switch.location.prefix,
                switches=[
                    SwitchReadForCore(comment=s.comment, ip_address=s.ip_address, snmp_oid=s.snmp_oid)
                    for s in switch.switches
                ],
            )
            for switch in core_switches
        ]

    async def update(self, schema: CoreSwitchUpdate, ip_address=None) -> CoreSwitch:
        stmt = (
            select(CoreSwitch, Location)
            .outerjoin(Location, Location.prefix == schema.prefix)
            .where(CoreSwitch.ip_address == ip_address)
        )
        result = await self.session.execute(stmt)
        core_switch, location = result.one_or_none()

        if core_switch is None:
            raise ValueError(f"Device: {ip_address} not found")

        if schema.prefix and location is None:
            raise ValueError(f"Location with prefix: {schema.prefix} not found")

        if location:
            core_switch.location_id = location.id

        for attr, value in schema.model_dump(exclude_none=True, exclude={"prefix"}).items():
            setattr(core_switch, attr, value)

        await self.session.commit()
        return core_switch

    async def delete(self, schema: CoreSwitchDelete) -> CoreSwitch:
        stmt = select(CoreSwitch).where(CoreSwitch.ip_address == schema.ip_address)
        result = await self.session.execute(stmt)
        core_switch = result.scalar_one_or_none()

        if core_switch is None:
            raise ValueError(f"Core switch: {schema.ip_address} не найден")

        related_records_stmt = select(Switch).where(Switch.core_switch_ip == core_switch.ip_address)
        related_records_result = await self.session.execute(related_records_stmt)
        related_records = related_records_result.scalars().all()

        if related_records:
            raise ValueError(f"Невозможно удалить устройство: {schema.ip_address} связано с другими записями.")

        await self.session.delete(core_switch)
        await self.session.commit()
        return core_switch

    async def get_snmp_params(self) -> List[Dict[str, str]]:
        """ """
        stmt = (
            select(CoreSwitch)
            .options(selectinload(CoreSwitch.switches).selectinload(Switch.ports_relation))
            .order_by(CoreSwitch.id)
        )

        result = await self.session.scalars(stmt)

        core_switches = result.all()
        formatted_result = []

        for core in core_switches:
            core_data = {"core_switch_ip": core.ip_address, "oid": core.snmp_oid, "switches": []}
            for switch in core.switches:
                switch_data = {
                    "target_ip": switch.ip_address,
                    "snmp_oid": switch.snmp_oid,
                    "ports": [port.port.port_number for port in switch.ports_relation],
                }
                core_data["switches"].append(switch_data)
            formatted_result.append(core_data)

        return formatted_result
