from contextlib import asynccontextmanager

import api
import uvicorn
from core.config import settings
from core.models import db_helper
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

description = """
Net-View API. 🚀


<details>
<summary>🌈ChangeLog🌈 [1.0.0] - 15.11.2024</summary>

<h1>🌟!important!🌟</h1>

<h3>1. Обновлена структура базы данных</h3>

<h4>Новые таблицы:</h4>
<ul>
    <li><strong>locations</strong>
        <ul>
            <li>id: <code>int</code></li>
            <li>name: <code>str</code></li>
            <li>prefix: <code>str</code></li>
            <li>Связные таблицы:
                <ul>
                    <li>switches</li>
                    <li>core_switches</li>
                </ul>
            </li>
        </ul>
    </li>
</ul>

<h4>Обновленные таблицы:</h4>
<ul>
    <li><strong>devices</strong>
        <ul>
            <li>nau_user: <code>str</code></li>
            <li>domain_user: <code>str</code></li>
            <li>remote_control: <code>str</code></li>
            <li>equipment: <code>str</code></li>
            <li>pc_name: <code>str</code></li>
        </ul>
    </li>
</ul>

<h3>2. Добавлены Эндпоинты Location</h3>
<ul>
    <li><strong>/api/v1/locations/</strong> - Получить все локации. (name, prefix)</li>
    <li><strong>/api/v1/locations/change/{prefix}</strong> - Изменить name или prefix локации.</li>
    <li><strong>/api/v1/locations/create</strong> - Создать локацию.</li>
    <li><strong>/api/v1/locations/delete/{prefix}</strong> - Удалить по (path)prefix. 
        Не удаляется, если есть связь с опорным коммутатором или коммутатором.
    </li>
</ul>
<p>Значения name и prefix должны быть уникальны и не равны null при создании нового объекта.</p>

<h3>3. Реализована передача ошибки 422 в ключ "msg"</h3>
<p>Пример передачи (<em>null</em>) в поле prefix:</p>
<p>Запрос на (<strong>/api/v1/locations/create</strong>):</p>
<pre><code>{
    "name": "Волжский",
    "prefix": null
}</code></pre>
<p>Ответ:</p>
<p>422 Error: Unprocessable Entity</p>
<pre><code>{
    "detail": [
        {
            "type": "string_type",
            "loc": [
                "body",
                "prefix"
            ],
            "msg": "Input should be a valid string",
            "input": null
        }
    ]
}</code></pre>
<p>Ключ "loc" - В каком поле.<br>
Ключ "msg" - Какая ошибка.<br>
Ключ "input" - Что ввёл клиент.</p>

<h1>Other</h1>

<h2>CoreSwitch</h2>
<ul>
    <li><strong>/api/v1/core_switches/all</strong> - Теперь возвращает поле (<em>"location_name"</em>)</li>
    <li><strong>/api/v1/core_switches/create</strong> - Теперь принимает поле для локации. (<em>"prefix"</em>)</li>
    <li><strong>/api/v1/core_switches/update/{ip_address}</strong> - Теперь принимает поле для локации. (<em>"prefix"</em>)</li>
    <li><strong>/api/v1/core_switches/delete</strong> - Теперь принимает поле ip-address (ранее "comment"). (<em>"ip-address"</em>)</li>
</ul>

<h2>Switch</h2>
<ul>
    <li><strong>/api/v1/switches/create</strong> - Подвязывается к location автоматически. (<em>"location_name"</em>)</li>
    <li><strong>/api/v1/switches/show-configures</strong> - Теперь возвращает поле (<em>"location_name"</em>)</li>
    <li><strong>/api/v1/switches/delete/{ip_address}</strong> - Теперь удаляется со всеми привязанными устройствами.</li>
</ul>

<h2>Device</h2>
<ul>
    <li><strong>/api/v1/devices/change/{ip_address}</strong> - Теперь добавляет prefix. Пример: "VLZ-{user_input}" (<em>"prefix"</em>)</li>
</ul>

<h2>SnmpControl</h2>
<ol>
    <li>Переписана логика, не прерывается при обходе всех устройств из базы данных, даже если они недоступны.</li>
    <li>Записывает в логи успешность операции для каждого переданного устройства.</li>
</ol>
<p>Логи:</p>
<pre><code>docker logs container_id</code></pre>

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
