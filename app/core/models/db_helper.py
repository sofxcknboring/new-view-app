from collections.abc import AsyncGenerator

from core.config import settings
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


class DataBaseHelper:
    """
    Помощник для работы с базой данных на основе SQLAlchemy с асинхронными операциями.

    Attr:
        engine (AsyncEngine): Асинхронный движок SQLAlchemy для работы с базой данных.
        session_factory (async_sessionmaker[AsyncSession]):
        Фабрика сессий для управления подключениями к базе данных.

    Params:
        url (str): URL для подключения к базе данных.
        echo (bool): Логировать SQL-запросы (по умолчанию False).
        echo_pool (bool): Включает или отключает вывод информации о пуле соединений (по умолчанию False).
        pool_size (int): Размер пула подключений (по умолчанию 50).
        max_overflow (int): Максимальное количество дополнительных подключений,
        которые могут быть созданы при нагрузке (по умолчанию 10).
    """

    def __init__(
        self,
        url: str,
        echo: bool = True,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        """
        Освобождает все ресурсы, связанные с движком базы данных.
        Это включает закрытие всех открытых соединений и освобождение памяти.
        """
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Генератор для получения асинхронной сессии базы данных.

        Return:
            AsyncGenerator[AsyncSession, None]: Генератор сессии базы данных.
        """
        async with self.session_factory() as session:
            yield session


db_helper = DataBaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)
