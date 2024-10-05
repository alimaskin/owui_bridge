# app/transfer.py
import asyncio
from app.db import Database
from app.sender import LotusClient
import logging
from datetime import datetime

async def transfer_data(db: Database, lotus: LotusClient):
    try:
        last_created_at = await db.get_last_created_at()
        logging.info(f"Last created_at: {last_created_at}")

        events = await db.fetch_new_events(last_created_at)
        logging.info(f"Fetched {len(events)} new events.")

        if not events:
            return

        # Отправляем батч событий
        try:
            response = await lotus.track_events_batch(events)
            # Проверка ответа и логика обновления состояния
            latest_created_at = max(event['created_at'] for event in events)
            await db.update_last_created_at(latest_created_at)
            logging.info(f"Updated last_created_at to {latest_created_at}")
        except Exception as e:
            logging.error(f"Error sending batch events: {e}")
            # Реализация DLQ или другой логики обработки неудачных отправок
    except Exception as e:
        logging.error(f"Unexpected error during transfer: {e}")

async def periodic_transfer(db: Database, lotus: LotusClient, interval_seconds=60):
    while True:
        try:
            await transfer_data(db, lotus)
        except Exception as e:
            logging.error(f"Unexpected error during transfer: {e}")
        await asyncio.sleep(interval_seconds)
