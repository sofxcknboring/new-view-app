from typing import List, Optional

from core.services.crud.crud_switch import CrudSwitch
from core.services.crud.helpers import get_crud
from fastapi import APIRouter, Depends, Path, Query
from schemas.device import DeviceResponse
from schemas.switch import SwitchCreate, SwitchResponse, SwitchUpdate

router = APIRouter(tags=["Switch"])

# Зависимость для работы с моделью Switch.
dep_crud_switch = get_crud(CrudSwitch)


@router.get("/", response_model=List[SwitchResponse])
async def get_switches(
    crud: CrudSwitch = Depends(dep_crud_switch),
    switch_name: Optional[str] = Query(None, description="Параметр для поиска коммутаторов по полю 'comment'."),
    switch_ip: Optional[str] = Query(None),
    status: Optional[bool] = Query(True),
    vlan: Optional[int] = Query(None),
) -> List[SwitchResponse]:
    """
    Args:
        crud: Объект класса CrudSwitch, для сессий к базе данных.
        switch_name: Параметр для поиска коммутаторов по полю "comment"
        switch_ip: Параметр для поиска по ip-адресу
        status: Параметр для вывода устройств по статусу.
        vlan: Параметр для вывода устройств по значению vlan
    Returns:
        List[SwitchResponse]: Список объектов Switch из базы данных.
    """
    switches = await crud.read()

    response_switches = []
    for switch in switches:
        if (switch_ip is None or switch.ip_address.startswith(switch_ip)) and (
            switch_name is None or switch.comment.startswith(switch_name)
        ):
            devices = [
                DeviceResponse(
                    ip_address=device.ip_address,
                    mac=device.mac,
                    port=device.port,
                    status=device.status,
                    vlan=device.vlan,
                    update_time=device.update_time,
                )
                for device in switch.devices
                if (status is None or device.status == status) and (vlan is None or device.vlan == vlan)
            ]
            if devices:
                response_switch = SwitchResponse(
                    comment=switch.comment,
                    ip_address=switch.ip_address,
                    core_switch_ip=switch.core_switch_ip,
                    devices=devices,
                )
                response_switches.append(response_switch)

    return response_switches


@router.post("/", response_model=bool)
async def create_switch(switch_create: SwitchCreate, crud: CrudSwitch = Depends(dep_crud_switch)) -> bool:
    """
    Returns:
        bool: Успешность операции
    """
    is_new_core_switch = await crud.create(schema=switch_create)
    return is_new_core_switch


@router.put("/", response_model=bool)
async def update_switch(switch_update: SwitchUpdate, crud: CrudSwitch = Depends(dep_crud_switch)) -> bool:
    """
    Returns:
        bool: Успешность операции
    """
    is_updated_switch = await crud.update(schema=switch_update)
    return is_updated_switch


@router.delete("/", response_model=bool)
async def delete_switch(switch_ip: SwitchCreate, crud: CrudSwitch = Depends(dep_crud_switch)) -> bool:
    """
    Returns:
        bool: Успешность операции
    """
    is_deleted_switch = await crud.delete(schema=switch_ip)
    return is_deleted_switch
