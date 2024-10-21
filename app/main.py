from contextlib import asynccontextmanager

import api
import uvicorn
from core.config import settings
from fastapi import FastAPI

from core.models import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Асинхронный контекстный менеджер для управления жизненным циклом приложения FastAPI.
    Функция выполняет логику на этапе старта и завершения работы приложения.
    Args:
        app (FastAPI): Экземпляр приложения FastAPI.

    Yields:
        None: Возвращает управление приложению между этапами запуска и завершения.
    """
    # start up logic
    yield
    # shutdown logic
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(api.router, prefix=settings.api.prefix)


if __name__ == "__main__":
    uvicorn.run("main:main_app", host=settings.run.host, port=settings.run.port, reload=True)
