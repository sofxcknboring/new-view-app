from typing import List, Sequence

from pydantic import ValidationError

from core.models import Device
from core.services.crud.crud_device import CrudDevice
from core.services.crud.helpers import get_crud
from fastapi import APIRouter, Depends, HTTPException
from schemas.device import DeviceRead, DeviceUpdate, DeviceQuery

router = APIRouter(tags=["Device"])


# Зависимость для работы с моделью
dep_crud_device = get_crud(CrudDevice)


@router.get("/", response_model=List[DeviceRead])
async def get_devices(
        crud: CrudDevice = Depends(dep_crud_device),
        queries: DeviceQuery = Depends()) -> Sequence[Device]:
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
        return devices
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/change/{ip_address}", response_model=DeviceRead)
async def change_workplace_name_by_ip_address(
    ip_address,
    device_update: DeviceUpdate, crud: CrudDevice = Depends(dep_crud_device)
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
        response = DeviceRead.from_orm(updated_device)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
