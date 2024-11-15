from typing import List, Sequence

from pydantic import ValidationError

from core.services.crud.crud_location import CrudLocation
from core.services.crud.helpers import get_crud
from fastapi import APIRouter, Depends, HTTPException
from schemas.location import LocationBase, LocationUpdate
from core.models import Location

router = APIRouter(tags=["Location"])

# Зависимость для работы с моделью
dep_crud_location = get_crud(CrudLocation)


@router.get("/", response_model=List[LocationBase])
async def get_locations(
        crud: CrudLocation = Depends(dep_crud_location)) -> Sequence[Location]:
    """
    В разработке, возможны ошибки.\n
    Returns:\n
        200: Возвращает список всех локаций.

    Raises:\n
        422: Ошибка валидации.
        500: Иная ошибка на стороне сервера.
    """
    try:
        locations = await crud.read()
        return locations
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/change/{prefix}", response_model=LocationBase)
async def update_location(
    prefix, location_update: LocationUpdate, crud: CrudLocation = Depends(dep_crud_location)
) -> LocationUpdate:
    """
    В разработке возможны ошибки.\n

    Изменить поля Location
    path -> prefix

    Returns:\n
        200 -> OK
        422 -> Ошибка валидации
        500 -> Location Update failed -> Location not found.
    """

    try:
        updated_device = await crud.update(schema=location_update, prefix=prefix)
        response = LocationUpdate.from_orm(updated_device)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", response_model=LocationBase)
async def create_location(location_create: LocationBase, crud: CrudLocation = Depends(dep_crud_location)) -> LocationBase:
    """
    Returns:\n
        200: SwitchResponse: OK -> Created Location

    Raises:\n
        409: Повторяющаяся запись.
        422: Передано невалидное значение в поле.
        500: Иная ошибка на стороне сервера.
    """
    try:
        new_location = await crud.create(schema=location_create)
        response = LocationBase.from_orm(new_location)
        return response
    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = error['loc']
            message = error['msg']
            errors.append({
                "field": field,
                "message": message
            })

        raise HTTPException(status_code=422, detail=errors)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/delete/{prefix}", response_model=LocationBase)
async def delete_switch(prefix: str, crud: CrudLocation = Depends(dep_crud_location)) -> LocationBase:
    """
    Удалить по префиксу.
    Returns:\n
        200: OK -> Deleted Location

    Raises:\n
        404: Location не найдена.
        500: Иная ошибка на стороне сервера.
    """
    try:
        deleted_location = await crud.delete(schema=prefix)
        response = LocationBase.from_orm(deleted_location)
        return response
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))