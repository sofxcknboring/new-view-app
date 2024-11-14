from contextlib import asynccontextmanager

import api
import uvicorn
from core.config import settings
from core.models import db_helper
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

description = """
Net-View API. 🚀

## CoreSwitch

На данный момент реализованы только CRUD операции:
* **Добавить новый опорный коммутатор**
* **Вернуть конфигурационные данные опорного коммутатора и коммутаторов**
* **Обновить данные об опорном коммутаторе**
* **Удалить опорный коммутатор** (_Не удаляет данные рекурсивно_)

## Switch

На данный момент реализованы только CRUD операции:
* **Добавить новый опорный коммутатор**
* **Вернуть все коммутаторы и устройства**(_реализована фильтрация по параметрам_)
* **Обновить данные об опорном коммутаторе**
* **Удалить коммутатор**(_Не удаляет данные рекурсивно_)

## Device
На данный момент реализованы только READ, UPDATE операции:
* **Вернуть все устройства**
* **Обновить данные об устройстве**

## Snmp Control
На данный момент реализован ручной запуск без параметров для отладки приложения
(_Требуется авторизация по API ключу_)

<details>
<summary>## ChangeLog</summary>

### [1.0.0] - 2023-10-01
- Первая версия API с базовыми CRUD операциями для CoreSwitch и Switch.
- Реализована возможность получения данных об устройствах.

### [1.1.0] - 2023-10-15
- Добавлены операции обновления для Device.
- Улучшена фильтрация при получении коммутаторов.

### [1.2.0] - 2023-10-20
- Добавлена поддержка SNMP контроля.
- Исправлены ошибки в обработке запросов.

</details>

"""


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
    title="Net-View-API",
    description=description,
    contact={
        "name": "Dev contact",
        "url": "https://mattermost.neovox.ru/ncc/messages/@v.a.mishurenko",
    },
    lifespan=lifespan,
)
main_app.include_router(api.router)


origins = [
    "https://grafana.danilenko.tech",
]

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
        workers=4,
        log_config="log_conf.yaml"
    )
