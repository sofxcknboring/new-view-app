# README

## install

1. Установите зависимости:
   ```bash
   poetry install
   ```

2. настройка .env
   ```python
    APP_CONFIG__DB__URL=postgresql+asyncpg://user:password@host:5432/database_name

    APP_CONFIG__SNMP__PORT=161
    APP_CONFIG__SNMP__USERNAME=...
    APP_CONFIG__SNMP__AUTH_KEY=...
    APP_CONFIG__SNMP__PRIV_KEY=...
    APP_CONFIG__SNMP__COMMUNITY=...


    APP_CONFIG__API_KEY=SECRET_KEY

   ```