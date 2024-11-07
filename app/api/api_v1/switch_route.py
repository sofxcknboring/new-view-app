from typing import List, Sequence

from core.models import Switch
from core.services.crud.crud_switch import CrudSwitch
from core.services.crud.helpers import get_crud
from fastapi import APIRouter, Depends
from schemas.switch import SwitchCreate, SwitchResponse, SwitchUpdate, SwitchReadQuery

router = APIRouter(tags=["Switch"])

# Зависимость для работы с моделью Switch.
dep_crud_switch = get_crud(CrudSwitch)


@router.get("/", response_model=List[SwitchResponse])
async def get_switches(
    crud: CrudSwitch = Depends(dep_crud_switch),
    queries: SwitchReadQuery = Depends(),
) -> Sequence[Switch]:
    """
    В разработке, возможны ошибки.\n

    Returns:\n
        Возвращает список коммутаторов отфильтрованных по параметрам(Query)
    """
    switches = await crud.read(queries)

    return switches


@router.post("/", response_model=bool)
async def create_switch(switch_create: SwitchCreate, crud: CrudSwitch = Depends(dep_crud_switch)) -> bool:
    """
    Returns:\n
        bool: Успешность операции
    """
    is_new_core_switch = await crud.create(schema=switch_create)
    return is_new_core_switch


@router.put("/", response_model=bool)
async def update_switch(switch_update: SwitchUpdate, crud: CrudSwitch = Depends(dep_crud_switch)) -> bool:
    """
    Returns:\n
        bool: Успешность операции
    """
    is_updated_switch = await crud.update(schema=switch_update)
    return is_updated_switch


@router.delete("/", response_model=bool)
async def delete_switch(switch_ip: SwitchCreate, crud: CrudSwitch = Depends(dep_crud_switch)) -> bool:
    """
    Returns:\n
        bool: Успешность операции
    """
    is_deleted_switch = await crud.delete(schema=switch_ip)
    return is_deleted_switch
