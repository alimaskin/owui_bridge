import asyncio
import logging
from app.transfer import periodic_transfer
from app.db import Database
from alembic.config import Config
from alembic import command
import os

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
    try:
        command.upgrade(alembic_cfg, "head")
        logging.info("Migrations applied successfully.")
    except Exception as e:
        logging.error(f"Failed to apply migrations: {e}")
        exit(1)

async def main():
    logging.basicConfig(level=logging.INFO)
    run_migrations()
    db = Database()
    await db.connect()
    await periodic_transfer(db)

if __name__ == "__main__":
    asyncio.run(main())
