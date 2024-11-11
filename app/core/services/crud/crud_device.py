from datetime import datetime, timezone
from typing import Sequence

from core.models import Device, Switch
from schemas.device import DeviceDataList, DeviceUpdate, DeviceQuery
from sqlalchemy import select

from .crud_base import BaseCRUD


class CrudDevice(BaseCRUD):

    async def create(self, schema: DeviceDataList):

        existing_device_query = await self.session.execute(select(Device))
        existing_devices = existing_device_query.scalars().all()

        new_device_keys = {(device.switch, device.port) for device in schema.devices}

        for device in existing_devices:
            key = (device.switch.ip_address, device.port)
            if key in new_device_keys:
                new_device_data = next(
                    d for d in schema.devices if d.switch == device.switch.ip_address and d.port == device.port
                )
                device.mac = new_device_data.mac
                device.vlan = new_device_data.vlan
                device.ip_address = new_device_data.ip
                device.status = True
                device.update_time = datetime.now(timezone.utc)
            else:
                device.status = False

        for new_device in schema.devices:
            switch_ip = new_device.switch
            switch = await self.session.execute(select(Switch).filter(Switch.ip_address == switch_ip))
            switch = switch.scalars().first()

            if not switch:
                raise ValueError(f"Switch with IP {switch_ip} not found.")

            existing_device_query = await self.session.execute(
                select(Device).filter(Device.switch_id == switch.id, Device.port == new_device.port)
            )
            existing_device = existing_device_query.scalars().first()

            if not existing_device:
                new_device_entry = Device(
                    workplace_number=None,
                    port=new_device.port,
                    mac=new_device.mac,
                    vlan=new_device.vlan,
                    ip_address=new_device.ip,
                    status=True,
                    update_time=datetime.now(timezone.utc),
                    switch_id=switch.id,
                )
                self.session.add(new_device_entry)

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
            raise ValueError(f'Device {ip_address} not found')

        for attr, value in schema.model_dump(exclude_none=True).items():
            setattr(device, attr, value)

        await self.session.commit()
        return device

    async def delete(self, schema):
        pass
