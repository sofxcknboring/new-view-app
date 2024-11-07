from typing import List, Sequence

from core.models import Device
from core.services.crud.crud_device import CrudDevice
from core.services.crud.helpers import get_crud
from fastapi import APIRouter, Depends, HTTPException
from schemas.device import DeviceRead, DeviceUpdate

router = APIRouter(tags=["Device"])


# Зависимость для работы с моделью
dep_crud_device = get_crud(CrudDevice)


@router.get("/", response_model=Sequence[Device])
async def get_devices(crud: CrudDevice = Depends(dep_crud_device)) -> Sequence[Device]:
    """
    В разработке возможны ошибки.
    Returns:
        Возвращает список всех устройств.
    """
    devices = await crud.read()
    return devices


@router.put("/", response_model=dict)
async def change_workplace_name_by_ip_address(
        device_update: DeviceUpdate,
        crud: CrudDevice = Depends(dep_crud_device)) -> dict:
    """
    В разработке возможны ошибки.

    Изменить поле "workplace_number" на устройстве.

    Returns:
        200 -> XX.XX.XX.XX is updated. New comment: "New comment"
        500 -> Device Update failed -> Device: XX.XX.XX.XX not found.
    """

    try:
        updated_device = await crud.update(schema=device_update)
        if updated_device:
            return {"message": f"{device_update.ip} is updated. New comment: {device_update.workplace_number}"}
        else:
            raise HTTPException(status_code=500, detail="Device Update failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

