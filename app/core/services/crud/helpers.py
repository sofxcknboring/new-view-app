from typing import Callable, Type, TypeVar, Any, Coroutine

from core.models import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .crud_base import BaseCRUD

CRUDType = TypeVar("CRUDType", bound=BaseCRUD)


def get_crud(crud_cls: Type[CRUDType]) -> Callable[[AsyncSession], Coroutine[Any, Any, CRUDType]]:
    """
    Получает функцию зависимости для создания экземпляра класса CRUD с использованием асинхронной сессии базы данных.

    Args:
        crud_cls: Класс CRUD, экземпляр которого нужно создать.

    Returns:
        Callable[[AsyncSession], Coroutine[Any, Any, CRUDType]]:
        Функция зависимости, которая возвращает экземпляр класса CRUD.
    """

    async def crud_instance(session: AsyncSession = Depends(db_helper.session_getter)) -> CRUDType:
        return crud_cls(session=session)

    return crud_instance
