from typing import List

from core.services.crud.crud_device import CrudDevice
from core.services.crud.helpers import get_crud
from fastapi import APIRouter, Depends
from schemas.device import DeviceRead, DeviceUpdate

router = APIRouter(tags=["Device"])


# Зависимость для работы с моделью
dep_crud_device = get_crud(CrudDevice)


@router.get("/", response_model=List[DeviceRead])
async def get_devices(crud: CrudDevice = Depends(dep_crud_device)) -> List[DeviceRead]:
    """
    Returns:
        List[DeviceRead]: Список объектов Device из базы данных.
    """
    devices = await crud.read()
    return devices


@router.put("/", response_model=bool)
async def update_device(device_update: DeviceUpdate, crud: CrudDevice = Depends(dep_crud_device)) -> DeviceRead:
    """
    Returns:
        bool: Успешность операции
    """
    is_updated_device = await crud.update(schema=device_update)
    return is_updated_device


