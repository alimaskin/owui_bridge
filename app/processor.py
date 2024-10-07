# app/processor.py

import asyncio
from app.db import Database
from app.sender import LotusClient
import logging
from sqlalchemy import select, and_
from app.models import EventStatus
from datetime import datetime

MAX_ATTEMPTS = 5  # Максимальное количество попыток отправки

async def process_events(db: Database, lotus: LotusClient):
    try:
        # Открываем сессию для чтения данных
        async with db.write_session_maker() as session:
            # Выбираем события со статусом 'new' или 'error' и попытками < MAX_ATTEMPTS
            stmt = select(EventStatus).where(
                and_(
                    EventStatus.status.in_(['new', 'error']),
                    EventStatus.attempts < MAX_ATTEMPTS
                )
            )
            result = await session.execute(stmt)
            events_status = result.scalars().all()

        if not events_status:
            logging.info("No events to process.")
            return

        logging.info(f"Processing {len(events_status)} events.")

        tasks = []
        for event_status in events_status:
            tasks.append(send_event(event_status, lotus, db))

        # Параллельная отправка событий
        await asyncio.gather(*tasks, return_exceptions=True)

    except Exception as e:
        logging.error(f"Error processing events: {e}")
        raise e

async def send_event(event_status: EventStatus, lotus: LotusClient, db: Database):
    event_data = event_status.event_data
    try:
        await lotus.track_event(event_data, event_status)

        # Если успешно, обновляем статус на 'sent'
        async with db.write_session_maker() as session:
            async with session.begin():
                # Получаем актуальный объект из базы данных
                db_event_status = await session.get(EventStatus, event_status.id)
                db_event_status.status = 'sent'
                db_event_status.attempts += 1
                db_event_status.last_error = None
                db_event_status.updated_at = datetime.utcnow()
                await session.commit()
                logging.info(f"Event {db_event_status.event_id} sent successfully.")

    except Exception as e:
        # При ошибке обновляем статус на 'error' и увеличиваем счетчик попыток
        async with db.write_session_maker() as session:
            async with session.begin():
                # Получаем актуальный объект из базы данных
                db_event_status = await session.get(EventStatus, event_status.id)
                db_event_status.status = 'error'
                db_event_status.attempts += 1
                db_event_status.last_error = str(e)
                db_event_status.updated_at = datetime.utcnow()

                # Если превышено MAX_ATTEMPTS, помечаем как 'failed'
                if db_event_status.attempts >= MAX_ATTEMPTS:
                    db_event_status.status = 'failed'
                    logging.error(f"Event {db_event_status.event_id} failed after max attempts.")

                await session.commit()
                logging.error(f"Error sending event {db_event_status.event_id}: {e}")
