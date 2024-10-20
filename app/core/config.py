from pydantic import BaseModel
from pydantic_settings import BaseSettings


class RunConfig(BaseModel):
    """
    Конфигурация для параметров запуска сервера.

    Атрибуты:
        host (str): IP-адрес хоста, на котором будет работать приложение (по умолчанию '0.0.0.0').
        port (int): Порт, на котором приложение будет слушать запросы (по умолчанию 8000).
    """

    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    """
    Конфигурация для префикса API.

    Атрибуты:
        prefix (str): Префикс для всех маршрутов API (по умолчанию '/api').
    """

    prefix: str = "/api"


class Setting(BaseSettings):
    """
    Основной класс для загрузки настроек приложения, объединяющий разные конфигурационные блоки.

    Атрибуты:
        run (RunConfig): Конфигурация параметров запуска сервера.
        api (ApiPrefix): Конфигурация префикса API.
    """

    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()


setting = Setting()
