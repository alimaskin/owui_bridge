# app/db.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from app.config import READ_DATABASE_URL, WRITE_DATABASE_URL
from app.models import Base, TransferState, Event
import logging
from datetime import datetime


class Database:
    def __init__(self):
        # Подключение для чтения
        self.read_engine = create_async_engine(READ_DATABASE_URL, echo=False)
        self.read_session_maker = sessionmaker(
            self.read_engine, expire_on_commit=False, class_=AsyncSession
        )

        # Подключение для записи
        self.write_engine = create_async_engine(WRITE_DATABASE_URL, echo=False)
        self.write_session_maker = sessionmaker(
            self.write_engine, expire_on_commit=False, class_=AsyncSession
        )

    async def connect(self):
        # Создаем таблицы в owui_bridge
        logging.info("Connecting to write database and creating tables...")
        async with self.write_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Connected successfully")
        # Инициализируем transfer_state
        await self.initialize()

    async def disconnect(self):
        await self.read_engine.dispose()
        await self.write_engine.dispose()

    async def initialize(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS transfer_state (
            id SERIAL PRIMARY KEY,
            last_created_at TIMESTAMP NOT NULL
        );
        """
        insert_initial_query = """
        INSERT INTO transfer_state (last_created_at)
        SELECT '1970-01-01T00:00:00Z'
        WHERE NOT EXISTS (SELECT 1 FROM transfer_state);
        """
        async with self.write_session_maker() as session:
            async with session.begin():
                await session.execute(text(create_table_query))
                await session.execute(text(insert_initial_query))
            logging.info("Initialized transfer_state table in owui_bridge.")

    async def fetch_new_events(self, last_created_at):
        query = """
            SELECT ob.created_at, ob.updated_at,
                   tr.id as trace_id,
                   ob.id as observe_id,
                   tr.user_id, 
                   ob.total_cost, 
                   ob.calculated_total_cost
              FROM public.observations ob
              JOIN public.traces tr ON ob.trace_id = tr.id
             WHERE ob.created_at > :last_created_at
             ORDER BY ob.created_at ASC
        """
        async with self.read_session_maker() as session:
            result = await session.execute(text(query), {'last_created_at': last_created_at})
            rows = result.mappings().all()
            return [dict(row) for row in rows]

    async def get_last_created_at(self):
        query = "SELECT last_created_at FROM transfer_state WHERE id = 1"
        async with self.write_session_maker() as session:
            result = await session.execute(text(query))
            row = result.mappings().first()
            return row['last_created_at'] if row else None

    async def update_last_created_at(self, new_time):
        query = "UPDATE transfer_state SET last_created_at = :new_time WHERE id = 1"
        async with self.write_session_maker() as session:
            await session.execute(text(query), {'new_time': new_time})
            await session.commit()
