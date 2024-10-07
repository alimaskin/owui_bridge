# main_dev.py

import asyncio
import logging
from app.transfer import transfer_data
from app.db import Database
from app.sender import LotusClient
from app.processor import process_events

async def main():
    logging.basicConfig(level=logging.DEBUG)
    db = Database()
    await db.connect()
    lotus_client = LotusClient()
    try:
        while True:
            # Трансфер данных из основной таблицы в event_status
            await transfer_data(db)
            # Обработка и отправка событий из event_status
            await process_events(db, lotus_client)
            await asyncio.sleep(60)  # Интервал между запусками (можно настроить)
    finally:
        await lotus_client.close()
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
