from typing import List, Optional

from core.services.crud.crud_core_sw import CrudCoreSwitch
from core.services.crud.helpers import get_crud
from fastapi import APIRouter, Depends, Query
from schemas.core_switch import CoreSwitchBase, CoreSwitchCreate, CoreSwitchRead, CoreSwitchUpdate

router = APIRouter(tags=["CoreSwitch"])

dep_crud_core_switch = get_crud(CrudCoreSwitch)


@router.get("/", response_model=list[CoreSwitchRead])
async def get_core_switches(crud: CrudCoreSwitch = Depends(dep_crud_core_switch)) -> List[CoreSwitchRead]:
    """
    Returns:
        List[CoreSwitchRead]: Список объектов CoreSwitch -> Switch из базы данных.
        CoreSwitchRead -> if switch -> SwitchRead
    """
    core_switches = await crud.read()
    return core_switches

# @router.get("/", response_model=list[dict])
# async def get_core_switches(
#         crud: CrudCoreSwitch = Depends(dep_crud_core_switch),
#         fields: Optional[List[str]] = Query(None, description="Comma-separated list of fields to return")
# ) -> List[dict]:
#     core_switches = await crud.read()
#
#     if fields:
#         field_set = set(fields)
#         # Создаем новые словари с только указанными полями
#         filtered_switches = [{field: getattr(switch, field) for field in field_set if hasattr(switch, field)} for switch
#                              in core_switches]
#         return filtered_switches
#
#     return core_switches


@router.post("/", response_model=bool)
async def create_core_switch(
    core_switch_create: CoreSwitchCreate, crud: CrudCoreSwitch = Depends(dep_crud_core_switch)
) -> bool:
    """
    Returns:
        bool: Успешность операции
    """
    is_new_core_switch = await crud.create(schema=core_switch_create)
    return is_new_core_switch


@router.put("/", response_model=bool)
async def update_core_switch(
    core_switch_update: CoreSwitchUpdate, crud: CrudCoreSwitch = Depends(dep_crud_core_switch)
) -> bool:
    """
    Returns:
        bool: Успешность операции
    """
    is_updated_core_switch = await crud.update(schema=core_switch_update)
    return is_updated_core_switch


@router.delete("/", response_model=bool)
async def delete_core_switch(
    core_switch_base: CoreSwitchBase, crud: CrudCoreSwitch = Depends(dep_crud_core_switch)
) -> bool:
    """
    Returns:
        bool: Успешность операции
    """
    is_deleted_core_switch = await crud.delete(schema=core_switch_base)
    return is_deleted_core_switch
