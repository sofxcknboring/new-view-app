from typing import List

from core.services.crud.crud_core_sw import CrudCoreSwitch, get_crud_core_switch
from fastapi import APIRouter, Depends
from schemas.core_switch import CoreSwitchCreate, CoreSwitchRead, CoreSwitchUpdate, CoreSwitchBase

router = APIRouter(tags=["CoreSwitch"])


@router.get("/", response_model=list[CoreSwitchRead])
async def get_core_switches(crud: CrudCoreSwitch = Depends(get_crud_core_switch)) -> List[CoreSwitchRead]:
    """
    Args:
        crud (CrudCoreSwitch): Зависимость, предоставляющая объект для работы с CoreSwitch.

    Returns:
        List[CoreSwitchRead]: Список объектов CoreSwitch из базы данных.
    """
    core_switches = await crud.read()
    return core_switches


@router.post("/", response_model=CoreSwitchRead)
async def create_core_switch(
    core_switch_create: CoreSwitchCreate, crud: CrudCoreSwitch = Depends(get_crud_core_switch)
) -> CoreSwitchRead:
    """
    Args:
        core_switch_create (CoreSwitchCreate): Данные для создания нового CoreSwitch.
        crud (CrudCoreSwitch): Зависимость для работы с CoreSwitch.

    Returns:
        CoreSwitchRead: Созданный объект CoreSwitch.
    """
    new_core_switch = await crud.create(schema=core_switch_create)
    return new_core_switch


@router.put("/", response_model=CoreSwitchRead)
async def update_core_switch(core_switch_update: CoreSwitchUpdate, crud: CrudCoreSwitch = Depends(get_crud_core_switch)
) -> CoreSwitchRead:
    """
    Args:
        core_switch_update (CoreSwitchUpdate): Данные для обновления CoreSwitch.
        crud (CrudCoreSwitch): Зависимость для работы с CoreSwitch.

    Returns:
        CoreSwitchRead: Обновлённый объект CoreSwitch.
    """
    updated_core_switch = await crud.update(schema=core_switch_update)
    return updated_core_switch


@router.delete("/", response_model=bool)
async def delete_core_switch(
        core_switch_base: CoreSwitchBase,
        crud: CrudCoreSwitch = Depends(get_crud_core_switch)) -> bool:
    """
    Args:
        core_switch_base: имя опорного коммутатора.
        crud (CrudCoreSwitch): Зависимость для работы с CoreSwitch.

    Returns:
        bool: Успешность операции удаления (True, если удалено, False, если объект не найден).
    """
    is_deleted_core_switch = await crud.delete(schema=core_switch_base)
    return is_deleted_core_switch
