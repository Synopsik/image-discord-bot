import asyncpg

async def execute(db_pool: asyncpg.Pool, query: str, *args):
    async with db_pool.acquire() as conn:
        await conn.execute(query, *args)

