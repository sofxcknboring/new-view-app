from contextlib import asynccontextmanager

import api
import uvicorn
from core.config import settings
from fastapi import FastAPI

from core.models.db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start up
    yield
    # shutdown
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(api.router, prefix=settings.api.prefix)


if __name__ == "__main__":
    uvicorn.run("main:main_app", host=settings.run.host, port=settings.run.port, reload=True)
