from datetime import datetime, timezone
from typing import Sequence


from core.models import Device, Switch
from schemas.device import DeviceUpdate, DeviceQuery, DevicesSnmpResponse
from sqlalchemy import select

from .crud_base import BaseCRUD


class CrudDevice(BaseCRUD):

    async def create(self, schema: DevicesSnmpResponse):

        switches = {}

        switch_query = await self.session.execute(
            select(Switch).where(Switch.ip_address.in_([s.switch for s in schema.switches]))
        )
        db_switches = switch_query.scalars().all()

        for switch in db_switches:
            switches[switch.ip_address] = switch

        for switch_data in schema.switches:
            switch_ip = switch_data.switch
            db_switch = switches.get(switch_ip)

            if not db_switch:
                raise ValueError(f"Switch with IP {switch_ip} not found.")

            existing_device_query = await self.session.execute(select(Device).where(Device.switch_id == db_switch.id))
            existing_devices = existing_device_query.scalars().all()
            existing_devices_by_mac = {device.mac: device for device in existing_devices}

            for new_schema_device in switch_data.devices:
                key = new_schema_device.mac
                if key in existing_devices_by_mac:

                    existing_device = existing_devices_by_mac[key]
                    existing_device.port = new_schema_device.port
                    existing_device.vlan = new_schema_device.vlan
                    existing_device.ip = new_schema_device.ip
                    existing_device.status = True
                    existing_device.update_time = datetime.now(timezone.utc)
                else:
                    new_device_entry = Device(
                        workplace_number=None,
                        port=new_schema_device.port,
                        mac=new_schema_device.mac,
                        vlan=new_schema_device.vlan,
                        ip_address=new_schema_device.ip,
                        status=True,
                        update_time=datetime.now(timezone.utc),
                        switch_id=db_switch.id,
                    )
                    self.session.add(new_device_entry)

            # Обновляем статус существующих устройств
            for existing_device in existing_devices:
                if existing_device.mac not in {device.mac for device in switch_data.devices}:
                    existing_device.status = False

        await self.session.commit()
        return True

    async def read(self, schema=DeviceQuery) -> Sequence[Device]:
        stmt = select(Device).order_by(Device.port)

        if schema.ip_address:
            stmt = stmt.where(Device.ip_address.ilike(f"%{schema.ip_address}%"))
        result = await self.session.scalars(stmt)
        devices = result.all()
        return devices

    async def update(self, schema: DeviceUpdate, ip_address=None) -> Device:
        stmt = select(Device).where(Device.ip_address == ip_address)
        result = await self.session.execute(stmt)
        device = result.scalar_one_or_none()

        if device is None:
            raise ValueError(f"Device {ip_address} not found")

        for attr, value in schema.model_dump(exclude_none=True).items():
            setattr(device, attr, value)

        await self.session.commit()
        return device

    async def delete(self, schema):
        pass
