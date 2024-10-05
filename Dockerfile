FROM python:3.11-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
COPY requirements.dev.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY app/ ./app
COPY alembic.ini .
COPY alembic/ ./alembic
COPY main_prod.py transfer.py ./

# Команда по умолчанию
CMD ["python", "main_prod.py"]
