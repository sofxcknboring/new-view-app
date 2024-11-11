from typing import List, Sequence

from pydantic import ValidationError

from core.models import Switch
from core.services.crud.crud_switch import CrudSwitch
from core.services.crud.helpers import get_crud
from fastapi import APIRouter, Depends, HTTPException
from schemas.switch import SwitchCreate, SwitchResponse, SwitchUpdate, SwitchReadQuery, SwitchRead

router = APIRouter(tags=["Switch"])

# Зависимость для работы с моделью Switch.
dep_crud_switch = get_crud(CrudSwitch)


@router.get("/devices", response_model=List[SwitchResponse])
async def get_switches(
    crud: CrudSwitch = Depends(dep_crud_switch),
    queries: SwitchReadQuery = Depends(),
) -> Sequence[Switch]:
    """
    В разработке, возможны ошибки.\n
    Returns:\n
        200: Возвращает список коммутаторов отфильтрованных по параметрам(Query)
    Raises:\n
        500: Иная ошибка на стороне сервера.
    """
    try:
        switches = await crud.read(queries)
        return switches
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/show-configures', response_model=List[SwitchRead])
async def get_switches_configures(
        crud: CrudSwitch = Depends(dep_crud_switch),
) -> List[SwitchRead]:
    switches_with_ports = await crud.get_switches_configures()
    switch_data = []
    for switch in switches_with_ports:
        switch_info = SwitchRead(
            id=switch['id'],
            ip_address=switch['ip_address'],
            snmp_oid=switch['snmp_oid'],
            core_switch_ip=switch['core_switch_ip'],
            excluded_ports=[
                ep.excluded_port.port_number for ep in switch['excluded_ports']
            ]
        )
        switch_data.append(switch_info)

    return switch_data


@router.post("/create", response_model=SwitchResponse)
async def create_switch(switch_create: SwitchCreate, crud: CrudSwitch = Depends(dep_crud_switch)) -> SwitchResponse:
    """
    Returns:\n
        200: SwitchResponse: Информация о созданном коммутаторе.

    Raises:\n
        409: Повторяющаяся запись.
        422: Передано невалидное значение в поле -> Подробнее в detail->msg.
        500: Иная ошибка на стороне сервера.
    """
    try:
        new_core_switch = await crud.create(schema=switch_create)
        response = SwitchResponse.from_orm(new_core_switch)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{ip_address}", response_model=SwitchResponse)
async def update_switch(ip_address, switch_update: SwitchUpdate, crud: CrudSwitch = Depends(dep_crud_switch)) -> SwitchResponse:
    """
    Returns:\n
        200: SwitchResponse: Информация об измененном коммутаторе.

    Raises:\n
        404: Коммутатор не найден.
        409: Повторяющаяся запись.
        422: Передано невалидное значение в поле -> Подробнее в detail->msg.
        500: Иная ошибка на стороне сервера.
    """
    try:
        updated_switch = await crud.update(schema=switch_update, ip_address=ip_address)
        response = SwitchResponse.from_orm(updated_switch)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{ip_address}", response_model=SwitchResponse)
async def delete_switch(ip_address: str, crud: CrudSwitch = Depends(dep_crud_switch)) -> SwitchResponse:
    """
    Returns:\n
        200: SwitchResponse: Информация об удаленном коммутаторе.

    Raises:\n
        404: Коммутатор не найден.
        500: Иная ошибка на стороне сервера.
    """
    try:
        deleted_switch = await crud.delete(schema=ip_address)
        response = SwitchResponse.from_orm(deleted_switch)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))