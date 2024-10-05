# app/sender.py
import asyncio
import lotus  # Импортируем SDK
from app.config import LOTUS_API_KEY, LOTUS_API_URL
from concurrent.futures import ThreadPoolExecutor
from app.models import Event
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from datetime import datetime
from decimal import Decimal

# Настройка логирования
logging.basicConfig(level=logging.INFO)


class LotusClient:
    def __init__(self):
        self.api_key = LOTUS_API_KEY
        print(f"API Key: {self.api_key}")  # Выводим API ключ для проверки
        self.host = LOTUS_API_URL  # Базовый URL без /api
        lotus.api_key = self.api_key  # Устанавливаем API ключ для SDK
        lotus.host = self.host  # Устанавливаем хост для SDK
        lotus.debug = False  # Включите режим отладки, если необходимо
        self.executor = ThreadPoolExecutor(max_workers=5)  # Создаём пул потоков для выполнения синхронных вызовов

    async def close(self):
        self.executor.shutdown(wait=True)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)  # Обработка всех исключений
    )
    async def track_event(self, event_data):
        # Создаём экземпляр модели Event
        event = Event(
            customer_id=event_data['user_id'],
            event_name='api_call',
            properties={
                "total_cost": event_data.get('total_cost'),
                "calculated_total_cost": event_data.get('calculated_total_cost')
            },
            idempotency_id=str(event_data['observe_id']),
            time_created=datetime.fromisoformat(event_data['created_at'].replace("Z", "+00:00"))
            # Преобразуем строку в datetime
        )

        # Определяем функцию для вызова SDK
        def send_event():
            try:
                response = lotus.track_event(
                    customer_id=event.customer_id,
                    event_name=event.event_name,
                    properties=event.properties,
                    idempotency_id=event.idempotency_id,
                    time_created=event.time_created.isoformat()  # SDK ожидает строку ISO формата
                )
                return response
            except Exception as e:
                raise e

        # Выполняем синхронный вызов в пуле потоков
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(self.executor, send_event)
            logging.info(f"Successfully sent event {event.idempotency_id}")
            return response
        except Exception as e:
            logging.error(f"Failed to send event {event.idempotency_id}: {e}")
            raise e

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def track_events_batch(self, events_data):
        tasks = []
        for event_data in events_data:
            tasks.append(self.track_event(event_data))
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response in responses:
            if isinstance(response, Exception):
                logging.error(f"Error sending event: {response}")

        return responses
