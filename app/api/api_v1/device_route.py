from typing import List, Sequence

from core.services.crud.crud_device import CrudDevice
from core.services.crud.helpers import get_crud
from device_sample import get_device_info
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from schemas.device import DeviceQuery, DeviceRead, DeviceUpdate, DeviceUpdateInfo

router = APIRouter(tags=["Device"])


# Зависимость для работы с моделью
dep_crud_device = get_crud(CrudDevice)


@router.get("/", response_model=List[DeviceRead])
async def get_devices(
    crud: CrudDevice = Depends(dep_crud_device), queries: DeviceQuery = Depends()
) -> Sequence[DeviceRead]:
    """
    В разработке, возможны ошибки.\n
    Returns:\n
        200: Возвращает список всех устройств по Query(ip-address)/Если не передан, все устройства.

    Raises:\n
        422: Ошибка валидации.
        500: Иная ошибка на стороне сервера.
    """
    try:
        devices = await crud.read(queries)
        return [
            DeviceRead(
                id=device.id,
                port=device.port,
                mac=device.mac,
                vlan=device.vlan.vlan if device.vlan else None,
                ip_address=device.ip_address,
                nau_user=device.nau_user,
                domain_user=device.domain_user,
                pc_name=device.pc_name,
                remote_control=device.remote_control,
                status=device.status,
                update_time=device.update_time,
                switch_id=device.switch_id,
            )
            for device in devices
        ]
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/change/{ip_address}", response_model=DeviceRead)
async def change_workplace_name_by_ip_address(
    ip_address, device_update: DeviceUpdate, crud: CrudDevice = Depends(dep_crud_device)
) -> DeviceRead:
    """
    В разработке возможны ошибки.\n

    Изменить поле "workplace_number" на устройстве.\n

    Returns:\n
        200 -> XX.XX.XX.XX is updated. New comment: "New comment"
        500 -> Device Update failed -> Device: XX.XX.XX.XX not found.
    """

    try:
        updated_device = await crud.update(schema=device_update, ip_address=ip_address)
        return DeviceRead(
            id=updated_device.id,
            port=updated_device.port,
            mac=updated_device.mac,
            vlan=updated_device.vlan.vlan if updated_device.vlan else None,
            ip_address=updated_device.ip_address,
            nau_user=updated_device.nau_user,
            domain_user=updated_device.domain_user,
            pc_name=updated_device.pc_name,
            remote_control=updated_device.remote_control,
            status=updated_device.status,
            update_time=updated_device.update_time,
            switch_id=updated_device.switch_id,
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_device_info/{ip_address}", response_model=DeviceRead)
async def update_device_info(ip_address: str, crud: CrudDevice = Depends(dep_crud_device)):
    try:
        new_device = get_device_info(ip_address=ip_address)
        schema = DeviceUpdateInfo(**new_device.to_dict())
        new_device_info = await crud.update_device_info(schema=schema, ip_address=ip_address)
        return DeviceRead(
            id=new_device_info.id,
            port=new_device_info.port,
            mac=new_device_info.mac,
            vlan=new_device_info.vlan.vlan if new_device_info.vlan else None,
            ip_address=new_device_info.ip_address,
            nau_user=new_device_info.nau_user,
            domain_user=new_device_info.domain_user,
            pc_name=new_device_info.pc_name,
            remote_control=new_device_info.remote_control,
            status=new_device_info.status,
            update_time=new_device_info.update_time,
            switch_id=new_device_info.switch_id,
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
