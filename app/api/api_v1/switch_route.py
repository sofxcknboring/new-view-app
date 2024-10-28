from typing import List

from core.services.crud.crud_switch import CrudSwitch
from core.services.crud.helpers import get_crud
from fastapi import APIRouter, Depends
from schemas.switch import SwitchCreate, SwitchIpAddress, SwitchRead, SwitchUpdate

router = APIRouter(tags=["Switch"])


# Зависимость для работы с моделью Switch.
dep_crud_switch = get_crud(CrudSwitch)


@router.get("/", response_model=List[SwitchRead])
async def get_switches(crud: CrudSwitch = Depends(dep_crud_switch)) -> List[SwitchRead]:
    """
    Returns:
        List[SwitchRead]: Список объектов Switch из базы данных.
    """
    switches = await crud.read()
    return switches


@router.post("/", response_model=bool)
async def create_switch(switch_create: SwitchCreate, crud: CrudSwitch = Depends(dep_crud_switch)) -> SwitchRead:
    """
    Returns:
        bool: Успешность операции
    """
    is_new_core_switch = await crud.create(schema=switch_create)
    return is_new_core_switch


@router.put("/", response_model=bool)
async def update_switch(switch_update: SwitchUpdate, crud: CrudSwitch = Depends(dep_crud_switch)) -> SwitchRead:
    """
    Returns:
        bool: Успешность операции
    """
    is_updated_switch = await crud.update(schema=switch_update)
    return is_updated_switch


@router.delete("/", response_model=bool)
async def delete_switch(switch_ip: SwitchIpAddress, crud: CrudSwitch = Depends(dep_crud_switch)) -> bool:
    """
    Returns:
        bool: Успешность операции
    """
    is_deleted_switch = await crud.delete(schema=switch_ip)
    return is_deleted_switch
