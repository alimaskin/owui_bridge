import asyncpg
from app.config import DATABASE_URL
import asyncio
import logging

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL, min_size=10, max_size=20)
        await self.initialize()

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
        async with self.pool.acquire() as connection:
            await connection.execute(create_table_query)
            await connection.execute(insert_initial_query)
            logging.info("Initialized transfer_state table.")

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
             WHERE ob.created_at > $1
             ORDER BY ob.created_at ASC
        """
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, last_created_at)
            return [dict(row) for row in rows]

    async def get_last_created_at(self):
        query = "SELECT last_created_at FROM transfer_state WHERE id = 1"
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query)
            return row['last_created_at']

    async def update_last_created_at(self, new_time):
        query = "UPDATE transfer_state SET last_created_at = $1 WHERE id = 1"
        async with self.pool.acquire() as connection:
            await connection.execute(query, new_time)
