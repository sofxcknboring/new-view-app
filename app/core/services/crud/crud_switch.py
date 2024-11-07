from typing import Dict, List, Sequence

from core.models import CoreSwitch, ExcludedPort, Switch, SwitchExcludedPort
from schemas.switch import SwitchCreate, SwitchUpdate, SwitchReadQuery
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .crud_base import BaseCRUD


class CrudSwitch(BaseCRUD):
    """
    Crud класс для коммутаторов.
    """

    async def create(self, schema: SwitchCreate) -> bool:
        existing_switch = await self.session.execute(select(Switch).where(Switch.ip_address == schema.ip_address))
        existing_switch = existing_switch.scalar_one_or_none()

        if existing_switch:
            raise ValueError(f"Switch with IP address {schema.ip_address} already exists.")

        stmt = select(CoreSwitch).where(CoreSwitch.ip_address == schema.core_switch_ip)
        result = await self.session.execute(stmt)
        core_switch = result.scalar_one_or_none()

        if core_switch is None:
            raise ValueError(f"Core switch: {schema.core_switch_ip} not found")

        switch = Switch(
            ip_address=schema.ip_address,
            comment=schema.comment,
            snmp_oid=schema.snmp_oid,
            core_switch_ip=schema.core_switch_ip,
            core_switch=core_switch,
        )

        self.session.add(switch)
        await self.session.commit()
        await self.session.refresh(switch)

        if schema.excluded_ports_relation:
            for port in schema.excluded_ports_relation:
                excluded_port = await self.session.execute(
                    select(ExcludedPort).where(ExcludedPort.port_number == int(port))
                )
                excluded_port = excluded_port.scalar_one_or_none()

                if excluded_port is None:
                    excluded_port = ExcludedPort(port_number=int(port))
                    self.session.add(excluded_port)
                    await self.session.flush()

                if excluded_port.id is None:
                    raise ValueError(f"Failed to retrieve ID for excluded port: {port}")

                switch_excluded_port = SwitchExcludedPort(switch_id=switch.id, excluded_port_id=excluded_port.id)
                self.session.add(switch_excluded_port)

        await self.session.commit()
        return True

    async def read(self, schema=SwitchReadQuery) -> Sequence[Switch]:
        stmt = select(Switch).options(selectinload(Switch.devices)).order_by(Switch.id)

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
                and (schema.device_vlan is None or str(schema.device_vlan) in str(device.vlan))
                and (schema.device_comment is None
                     or (device.workplace_number is not None and schema.device_comment in device.workplace_number))
                and (schema.device_ip_address is None or schema.device_ip_address in device.ip_address)
                and (schema.device_mac is None or schema.device_mac.upper() in device.mac)
            ]
            if switch.devices:
                switches_result.append(switch)

        return switches_result


    async def update(self, schema: SwitchUpdate) -> bool:
        stmt = select(Switch).where(Switch.ip_address == schema.ip_address)
        result = await self.session.execute(stmt)
        switch = result.scalar_one_or_none()

        if switch is None:
            raise ValueError(f"Switch: {schema.ip_address} not found")

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

        for excluded_port in switch.excluded_ports_relation:
            await self.session.delete(excluded_port)

        if schema.excluded_ports_relation:
            for port in schema.excluded_ports_relation:
                excluded_port = await self.session.execute(
                    select(ExcludedPort).where(ExcludedPort.port_number == int(port))
                )
                excluded_port = excluded_port.scalar_one_or_none()

                if excluded_port is None:
                    excluded_port = ExcludedPort(port_number=int(port))
                    self.session.add(excluded_port)
                    await self.session.flush()

                if excluded_port.id is None:
                    raise ValueError(f"Failed to retrieve ID for excluded port: {port}")

                switch_excluded_port = SwitchExcludedPort(switch_id=switch.id, excluded_port_id=excluded_port.id)
                self.session.add(switch_excluded_port)

        await self.session.commit()
        return True

    async def delete(self, schema: SwitchCreate) -> bool:
        stmt = select(Switch).where(Switch.ip_address == schema.ip_address)
        result = await self.session.execute(stmt)
        switch = result.scalar_one_or_none()

        if switch is None:
            return False

        for excluded_port in switch.excluded_ports_relation:
            await self.session.delete(excluded_port)

        await self.session.delete(switch)
        await self.session.commit()
        return True

    async def get_snmp_params(self) -> List[Dict]:
        """
        Возвращает список с параметрами для запроса к SNMP-агенту.
        Returns:
            [
                {
                    'ip_address': 192.168.0.1,
                    'snmp_oid': '1.3.6......',
                    'excluded_ports': [1,2,3,4,5,6,....]
                }
            ]
        """
        result = await self.session.execute(select(Switch).options(selectinload(Switch.excluded_ports_relation)))
        switches_data = []
        for switch in result.scalars().all():
            excluded_ports = [port.excluded_port.port_number for port in switch.excluded_ports_relation]
            switches_data.append(
                {"ip_address": switch.ip_address, "snmp_oid": switch.snmp_oid, "excluded_ports": excluded_ports}
            )
        return switches_data
