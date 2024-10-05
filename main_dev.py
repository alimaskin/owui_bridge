# main_dev.py
import asyncio
import logging
from app.transfer import periodic_transfer
from app.db import Database
from app.sender import LotusClient

async def main():
    logging.basicConfig(level=logging.INFO)
    db = Database()
    await db.connect()
    lotus_client = LotusClient()
    try:
        await periodic_transfer(db, lotus_client)
    finally:
        await lotus_client.close()

if __name__ == "__main__":
    asyncio.run(main())
