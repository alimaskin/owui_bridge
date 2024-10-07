# app/sender.py

import asyncio
import lotus
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
from dateutil.parser import parse

logging.basicConfig(level=logging.DEBUG)

class LotusClient:
    def __init__(self):
        self.api_key = LOTUS_API_KEY
        self.host = LOTUS_API_URL
        lotus.api_key = self.api_key
        lotus.host = self.host
        lotus.debug = True  # Включаем режим отладки
        lotus.sync_mode = False  # Включаем асинхронный режим
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def close(self):
        self.executor.shutdown(wait=True)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def track_event(self, event_data, event_status):
        try:
            if isinstance(event_data['created_at'], datetime):
                time_created = event_data['created_at']
            else:
                try:
                    time_created = parse(event_data['created_at'])
                except Exception as e:
                    logging.error(f"Error parsing 'created_at': {event_data['created_at']} - {e}")
                    raise e

            # Проверяем и преобразуем свойства
            properties = {}
            if event_data.get('total_cost') is not None:
                properties['total_cost'] = float(event_data.get('total_cost'))
            if event_data.get('calculated_total_cost') is not None:
                properties['calculated_total_cost'] = float(event_data.get('calculated_total_cost'))

            # Создаём экземпляр события
            event = Event(
                customer_id=str(event_data['user_id']),
                event_name='api_call',
                properties=properties,
                idempotency_id=str(event_status.event_id),  # Используем event_status.event_id
                time_created=time_created
            )

            # Фильтруем None значения в properties
            event.properties = {k: v for k, v in event.properties.items() if v is not None}

            # Проверяем, что все поля заполнены
            if not event.customer_id:
                logging.error("customer_id is missing or empty.")
            if not event.idempotency_id:
                logging.error("idempotency_id is missing or empty.")

            # Определяем функцию для вызова SDK
            def send_event():
                try:
                    # Форматируем time_created
                    time_created_formatted = event.time_created.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

                    event_payload = {
                        "customer_id": event.customer_id,
                        "event_name": event.event_name,
                        "properties": event.properties,
                        "idempotency_id": event.idempotency_id,
                        "time_created": time_created_formatted
                    }
                    logging.debug(f"Event payload: {event_payload}")
                    response = lotus.track_event(**event_payload)
                    return response
                except Exception as e:
                    logging.error(f"Exception in send_event: {e}")
                    raise e

            # Выполняем синхронный вызов в пуле потоков
            loop = asyncio.get_running_loop()
            try:
                response = await loop.run_in_executor(self.executor, send_event)
                logging.info(f"Successfully sent event {event.idempotency_id}")
                return response
            except Exception as e:
                logging.error(f"Failed to send event {event.idempotency_id}: {e}")
                raise e
        except Exception as e:
            logging.error(f"Exception in track_event for event {event_status.event_id}: {e}")
            raise e

