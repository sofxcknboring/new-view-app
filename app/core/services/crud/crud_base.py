from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession


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
    async def update(self, param, schema):
        pass

    @abstractmethod
    async def delete(self, param):
        pass
