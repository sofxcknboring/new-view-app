from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    """
    Конфигурация для параметров запуска сервера.

    Attributes:
        host (str): IP-адрес хоста, на котором будет работать приложение (по умолчанию '0.0.0.0').
        port (int): Порт, на котором приложение будет слушать запросы (по умолчанию 8000).
    """

    host: str = "0.0.0.0"
    port: int = 8000


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    core_switches: str = "/core_switches"
    switches: str = "/switches"
    devices: str = "/devices"


class ApiPrefix(BaseModel):
    """
    Конфигурация для префикса API.

    Attributes:
        prefix (str): Префикс для всех маршрутов API (по умолчанию '/api').
        v1 (str): Префикс для маршрутов V1.
    """

    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DataBaseConfig(BaseModel):
    """
    Конфигурация для подключения к базе данных PostgreSQL.

    Attributes:
        url (PostgresDsn): URL для подключения к базе данных в формате PostgresDsn.
        echo (bool): Логировать SQL-запросы (по умолчанию False).
        echo_pool (bool): Включает или отключает вывод информации о пуле соединений (по умолчанию False).
        pool_size (int): Размер пула подключений (по умолчанию 50).
        max_overflow (int): Максимальное количество дополнительных подключений,
        которые могут быть созданы при нагрузке (по умолчанию 10).
    """

    url: PostgresDsn
    echo: bool = True
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class SnmpConfig(BaseModel):
    """
    Конфигурация для подключения к SNMPv3 агенту.

    Attributes:
        port (str): Порт для подключения к SNMP агенту.
        username (str): Имя пользователя для аутентификации.
        auth_key (str): Ключ аутентификации для SNMPv3.
        priv_key (str): Ключ для шифрования данных (privacy key).
        community (str): Сообщество для SNMP (если используется SNMPv2c).
    """

    port: str
    username: str
    auth_key: str
    priv_key: str
    community: str


class Setting(BaseSettings):
    """
    Основной класс настроек приложения, объединяющий все конфигурации.

    Attributes:
        run (RunConfig): Конфигурация параметров запуска сервера.
        api (ApiPrefix): Конфигурация префикса для API маршрутов.
        db (DataBaseConfig): Конфигурация для подключения к базе данных.
        snmp (SnmpConfig): Конфигурация для SNMP подключения.
        api_key (str): API ключ для авторизации.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DataBaseConfig
    snmp: SnmpConfig
    api_key: str


settings = Setting()