from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.switch import SwitchIpAddress


class BaseCRUD(ABC):

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def create(self, schema):
        pass

    @abstractmethod
    async def read(self, schema):
        pass

    @abstractmethod
    async def update(self, schema, query=None):
        pass

    @abstractmethod
    async def delete(self, schema):
        pass
