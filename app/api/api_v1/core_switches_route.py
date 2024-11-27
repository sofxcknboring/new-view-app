from typing import List


from core.services.crud.crud_core_sw import CrudCoreSwitch
from core.services.crud.helpers import get_crud
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from schemas.core_switch import (CoreSwitchCreate, CoreSwitchDelete, CoreSwitchRead,
                                 CoreSwitchResponse, CoreSwitchUpdate)
from sqlalchemy.exc import IntegrityError

router = APIRouter(tags=["CoreSwitch"])

dep_crud_core_switch = get_crud(CrudCoreSwitch)


@router.get("/all", response_model=list[CoreSwitchRead])
async def get_core_switches(crud: CrudCoreSwitch = Depends(dep_crud_core_switch)) -> List[CoreSwitchRead]:
    """
    В разработке, возможны ошибки.\n
    Returns:\n
        200: Возвращает список опорных коммутаторов и привязанных к нему коммутаторов.
    Raises:\n
        500: Иная ошибка на стороне сервера.
    """
    try:
        core_switches = await crud.read()
        return core_switches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", response_model=CoreSwitchResponse)
async def create_core_switch(
    core_switch_create: CoreSwitchCreate, crud: CrudCoreSwitch = Depends(dep_crud_core_switch)
) -> CoreSwitchResponse:
    """
    В разработке, возможны ошибки.\n
    Создает новый опорный коммутатор.

    Examples:\n
    ```json
    {
      "prefix": "Префикс Location,
      "ip_address": "192.168.1.1"
    }
    ```

    Returns:\n
        200: CoreSwitchResponse: Информация о созданном коммутаторе.

    Raises:\n
        409: Повторяющаяся запись.
        422: Передано невалидное значение в поле -> Подробнее в detail->msg.
        500: Иная ошибка на стороне сервера.
    """
    try:
        new_core_switch = await crud.create(schema=core_switch_create)
        response = CoreSwitchResponse.from_orm(new_core_switch)
        return response
    except IntegrityError as e:
        if "ix_core_switches_ip_address" in str(e.orig):
            raise HTTPException(
                status_code=409,
                detail=f"Ошибка: IP-адрес {core_switch_create.ip_address} уже существует в базе данных.",
            ) from e
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update/{ip_address}", response_model=CoreSwitchResponse)
async def update_core_switch(
    ip_address, core_switch_update: CoreSwitchUpdate, crud: CrudCoreSwitch = Depends(dep_crud_core_switch)
) -> CoreSwitchResponse:
    """
    В разработке, возможны ошибки.\n
    Изменить опорный коммутатор.
    Returns:\n
        200: CoreSwitchResponse: Информация об измененном опорном коммутаторе.

    Raises:\n
        404: Коммутатор не найден.
        409: Повторяющаяся запись.
        422: Передано невалидное значение в поле -> Подробнее в detail->msg.
        500: Иная ошибка на стороне сервера.
    """
    try:
        updated_core_switch = await crud.update(schema=core_switch_update, ip_address=ip_address)
        response = CoreSwitchResponse.from_orm(updated_core_switch)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError as e:
        if "ix_core_switches_ip_address" in str(e.orig):
            raise HTTPException(
                status_code=409,
                detail=f"Ошибка: IP-адрес {core_switch_update.ip_address} уже существует в базе данных.",
            ) from e
        elif "ix_core_switches_name" in str(e.orig):
            raise HTTPException(
                status_code=409, detail=f"Ошибка: Имя {core_switch_update.name} уже существует в базе данных."
            ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete", response_model=CoreSwitchResponse)
async def delete_core_switch(
    core_switch_delete: CoreSwitchDelete, crud: CrudCoreSwitch = Depends(dep_crud_core_switch)
) -> CoreSwitchResponse:
    """
    В разработке, возможны ошибки.\n
    Удалить опорный коммутатор по ip-адресу.
    Returns:\n
        200: CoreSwitchResponse: Информация об удаленном опорном коммутаторе.

    Raises:\n
        404: Коммутатор не найден.
        409: Невозможно удалить устройство name, связано с другими записями
        422: Передано невалидное значение в поле -> Подробнее в detail->msg.
        500: Иная ошибка на стороне сервера.
    """
    try:
        deleted_core_switch = await crud.delete(schema=core_switch_delete)
        response = CoreSwitchResponse.from_orm(deleted_core_switch)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        if "Core switch" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        else:
            raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
