from typing import Dict, List

from core.models import CoreSwitch, Device, Port, Switch, SwitchPort
from schemas.switch import SwitchCreate, SwitchReadQuery, SwitchUpdate
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..snmp import SnmpV2
from ..snmp.snmp_formatters import SwitchFormatter
from .crud_base import BaseCRUD


class CrudSwitch(BaseCRUD):
    """
    Crud класс для коммутаторов.
    """

    async def create(self, schema: SwitchCreate) -> Switch:
        try:
            switch_walker = SnmpV2(format_class=SwitchFormatter)
            switch_name = await switch_walker.get_sys_descr(schema.ip_address)
            switch_ports = await switch_walker.get_port_vlan_table(schema.ip_address)
        except Exception:
            raise

        else:
            stmt = select(Switch).where(Switch.ip_address == schema.ip_address)
            result = await self.session.execute(stmt)
            switch = result.scalar_one_or_none()

            if switch:
                raise ValueError(f"Switch with IP address {schema.ip_address} already exists.")

            stmt = select(CoreSwitch).where(CoreSwitch.ip_address == schema.core_switch_ip)
            result = await self.session.execute(stmt)
            core_switch = result.scalar_one_or_none()
            if core_switch is None:
                raise ValueError(f"Core switch: {schema.core_switch_ip} not found")

            switch = Switch(
                ip_address=schema.ip_address,
                comment=switch_name,
                core_switch_ip=schema.core_switch_ip,
                core_switch=core_switch,
                location_id=core_switch.location_id,
            )

            self.session.add(switch)
            await self.session.commit()
            await self.session.refresh(switch)

            for port in switch_ports:
                if port:
                    db_port = await self.session.execute(select(Port).where(Port.port_number == int(port)))
                    db_port = db_port.scalar_one_or_none()
                    if db_port is None:
                        db_port = Port(port_number=int(port))
                        self.session.add(db_port)
                        await self.session.flush()

                    if db_port.id is None:
                        raise ValueError(f"Failed to retrieve ID for db port: {port}")

                    switch_port = SwitchPort(switch_id=switch.id, port_id=db_port.id)
                    self.session.add(switch_port)
                else:
                    continue

            await self.session.commit()
            await self.session.refresh(switch)
            return switch

    async def read(self, schema=SwitchReadQuery) -> list[Switch]:
        stmt = select(Switch).options(selectinload(Switch.devices).selectinload(Device.vlan))

        if schema.switch_comment:
            stmt = stmt.where(Switch.comment.ilike(f"%{schema.switch_comment}%"))
        if schema.ip_address:
            stmt = stmt.where(Switch.ip_address.ilike(f"%{schema.ip_address}%"))

        result = await self.session.scalars(stmt)
        switches = result.all()

        switches_result = []

        for switch in switches:
            switch.devices = [
                device
                for device in switch.devices
                if (schema.device_status is None or device.status == schema.device_status)
                and (schema.device_vlan is None or str(schema.device_vlan) in str(device.vlan.vlan))
                and (
                    schema.device_comment is None
                    or (device.workplace_number is not None and schema.device_comment in device.workplace_number)
                )
                and (schema.device_ip_address is None or schema.device_ip_address in device.ip_address)
                and (schema.device_mac is None or schema.device_mac.upper() in device.mac)
            ]
            if switch.devices:
                switches_result.append(switch)
        return list(switches_result)

    async def get_switches_configures(self) -> List[Dict]:
        stmt = select(Switch).options(selectinload(Switch.ports_relation), selectinload(Switch.location))

        switches = await self.session.execute(stmt)
        switches = switches.scalars().all()
        switch_data = []
        for switch in switches:
            switch_info = {
                "id": switch.id,
                "comment": switch.comment,
                "ip_address": switch.ip_address,
                "snmp_oid": switch.snmp_oid,
                "core_switch_ip": switch.core_switch_ip,
                "devices_count": len(switch.devices),
                "ports": switch.ports_relation,
                "location_name": switch.location.name,
            }
            switch_data.append(switch_info)

        return switch_data

    async def update(self, schema: SwitchUpdate, ip_address=None) -> Switch:
        stmt = select(Switch).where(Switch.ip_address == ip_address)
        result = await self.session.execute(stmt)
        switch = result.scalar_one_or_none()
        if switch:
            if schema.ip_address is not None:
                switch.ip_address = schema.ip_address

            if schema.comment is not None:
                switch.comment = schema.comment

            if schema.snmp_oid is not None:
                switch.snmp_oid = schema.snmp_oid

            if schema.core_switch_ip is not None:
                core_switch = await self.session.execute(
                    select(CoreSwitch).where(CoreSwitch.ip_address == schema.core_switch_ip)
                )
                core_switch = core_switch.scalar_one_or_none()

                if core_switch is None:
                    raise ValueError(f"Core switch: {schema.core_switch_ip} not found.")

                switch.core_switch = core_switch
        else:
            raise ValueError(f"Switch: {ip_address} not found")

        await self.session.commit()
        await self.session.refresh(switch)
        return switch

    async def delete(self, schema) -> Switch:
        stmt = select(Switch).where(Switch.ip_address == schema)
        result = await self.session.execute(stmt)
        switch = result.scalar_one_or_none()

        if switch is None:
            raise ValueError(f"Switch {schema} not found")

        for excluded_port in switch.ports_relation:
            await self.session.delete(excluded_port)

        for device in switch.devices:
            await self.session.delete(device)
        await self.session.delete(switch)
        await self.session.commit()
        return switch
