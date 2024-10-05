# Langfuse to Lotus Data Transfer Service

## Описание

Сервис для передачи данных из `langfuse` в `lotus`. Он извлекает новые записи из базы данных PostgreSQL и отправляет их в сервис `lotus` через API, обеспечивая гарантированную доставку и идемпотентность.

## Установка и Запуск

### Разработка (Development)

1. **Клонировать репозиторий**:
    ```bash
    git clone https://github.com/alimaskin/owui_bridge.git
    cd owui_bridge
    ```

2. **Создать и активировать виртуальное окружение**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Установить зависимости**:
    ```bash
    pip install -r requirements.dev.txt
    ```

4. **Настроить переменные окружения**:
    - Создайте файл `.env` на основе `.env.example` и заполните необходимые значения.

5. **Применить миграции**:
    ```bash
    alembic upgrade head
    ```

6. **Запустить сервис**:
    ```bash
    python main_dev.py
    ```

### Продакшен (Production)

1. **Настроить переменные окружения**:
    - Создайте файл `.env.prod` на основе `.env.example` и заполните необходимые значения.

2. **Сборка и запуск контейнеров**:
    ```bash
    docker-compose up --build -d
    ```

3. **Проверка состояния сервисов**:
    ```bash
    docker-compose ps
    docker-compose logs -f app
    ```

## Миграции

Используется Alembic для управления миграциями базы данных.

- **Создание новой миграции**:
    ```bash
    alembic revision -m "Описание миграции"
    ```

- **Применение миграций**:
    ```bash
    alembic upgrade head
    ```

## Логирование и Мониторинг

Логи выводятся в консоль. Для продакшен-среды настроена ротация логов через Docker.

## Тестирование

Запуск тестов:
```bash
pytest
