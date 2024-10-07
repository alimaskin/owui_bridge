# app/transfer.py

from app.db import Database
from app.utils import make_json_serializable
import logging
from datetime import datetime
from app.models import EventStatus
import uuid


async def transfer_data(db: Database):
    try:
        last_created_at = await db.get_last_created_at()
        logging.info(f"Last created_at: {last_created_at}")

        events = await db.fetch_new_events(last_created_at)
        logging.info(f"Fetched {len(events)} new events.")

        if not events:
            logging.info("No new events to transfer.")
            return

        # Сохраняем события в таблицу event_status
        logging.info("Saving events to event_status...")
        async with db.write_session_maker() as session:
            async with session.begin():
                for event_data in events:
                    event_id = str(uuid.uuid4())

                    # Преобразуем event_data в JSON-сериализуемый формат
                    serializable_data = make_json_serializable(event_data)
                    logging.debug(f"Serializable event_data: {serializable_data}")

                    event_status = EventStatus(
                        event_id=event_id,
                        event_data=serializable_data,
                        status='new'
                    )
                    session.add(event_status)
            await session.commit()
            logging.info("Events saved to event_status.")

        # Обновляем last_created_at после успешного сохранения событий
        latest_created_at = max(event['created_at'] for event in events)
        await db.update_last_created_at(latest_created_at)
        logging.info(f"Updated last_created_at to {latest_created_at}")

    except Exception as e:
        logging.error(f"Unexpected error during transfer: {e}")
        raise e
