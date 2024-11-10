# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем poetry
ENV POETRY_VERSION=1.8.0
RUN pip install poetry==$POETRY_VERSION

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы poetry
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN poetry install --no-root --no-dev

# Копируем исходный код приложения
COPY app .

# Копируем файл .env
COPY app/.env ./

# Указываем команду для запуска приложения
CMD ["poetry", "run", "python", "main.py"]
