from typing import Annotated

from core.models import db_helper
from core.services.crud.crud_core_sw import CrudCoreSwitch
from fastapi import APIRouter, Depends, HTTPException
from schemas.core_switch import CoreSwitchCreate, CoreSwitchRead, CoreSwitchUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["CoreSwitch"])


def get_crud(session: AsyncSession = Depends(db_helper.session_getter)):
    return CrudCoreSwitch(session=session)



@router.get("/", response_model=list[CoreSwitchRead])
async def get_core_switches(crud_core_switch: CrudCoreSwitch = Depends(get_crud)):
    core_switches = await crud_core_switch.read()
    return core_switches

#
# @router.get("/", response_model=list[CoreSwitchRead])
# async def get_core_switches(
#     session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
# ):
#     try:
#         crud_core_switch = CrudCoreSwitch(session=session)
#         core_switches = await crud_core_switch.read()
#         return core_switches
#     except Exception as e:
#         raise HTTPException(f"Error: {e}")


@router.post("/", response_model=CoreSwitchRead)
async def create_core_switches(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    core_switch_create: CoreSwitchCreate,
):
    try:
        crud_core_switch = CrudCoreSwitch(session=session)
        new_core_switch = await crud_core_switch.create(schema=core_switch_create)
        return new_core_switch
    except Exception as e:
        raise HTTPException(f"Error: {e}")


@router.put("/", response_model=CoreSwitchRead)
async def update_core_switches(
    core_switch_ip: str,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    core_switch_update: CoreSwitchUpdate,
):
    try:
        crud_core_switch = CrudCoreSwitch(session=session)
        upd_core_switch = await crud_core_switch.update(
            core_switch_ip=core_switch_ip,
            schema=core_switch_update)
        return upd_core_switch
    except Exception as e:
        raise HTTPException(f"Error: {e}")


@router.delete("/", response_model=bool)
async def delete_core_switches(
    core_switch_ip: str,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    crud_core_switch = CrudCoreSwitch(session=session)
    is_del_core_switch = await crud_core_switch.delete(core_switch_ip=core_switch_ip)
    if not is_del_core_switch:
        raise ValueError(f"Core switch: {core_switch_ip} not found")
    return is_del_core_switch
