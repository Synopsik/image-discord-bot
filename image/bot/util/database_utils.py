import asyncio
import logging
import os.path
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

import aiosqlite

logger = logging.getLogger(__name__) # Probably want to change this?

class SQLiteManager:
    def __init__(self, db_path: str=None):
        if db_path is None:
            # Get the dir where this file is
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Create db dir relative to this file
            db_dir = os.path.join(current_dir, "database")
            os.makedirs(db_dir, exist_ok=True)
            self.db_path = os.path.join(db_dir, "logs.db")
        else:
            self.db_path = db_path
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
        self._lock = asyncio.Lock()
        
        
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for database connections with proper locking"""
        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                # Enable WAL mode for better concurrent access
                await db.execute("PRAGMA journal_mode=WAL")
                # Enable foreign keys
                await db.execute("PRAGMA foreign_keys=ON")
                yield  db
                
    async def execute(self, query: str, *args) -> None:
        """Execute a query that doesn't return data"""
        async with self.get_connection() as db:
            await db.execute(query, args)
            await db.commit()
                
    async def fetch_one(self, query: str, *args) -> Optional[aiosqlite.Row]:
        """Fetch a single record"""
        async with self.get_connection() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, args) as cursor:
                return await cursor.fetchone()

    async def fetch_many(self, query: str, *args) -> List[aiosqlite.Row]:
        """Fetch multiple records"""
        async with self.get_connection() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, args) as cursor:
                return await cursor.fetchall()

    async def execute_many(self, query: str, args_list: List[tuple]) -> None:
        """Execute a query with multiple parameter sets (batch operations)"""
        async with self.get_connection() as db:
            await db.executemany(query, args_list)
            await db.commit()

    async def execute_script(self, script: str) -> None:
        """Execute SQL script (for setup)"""
        async with self.get_connection() as db:
            await db.executescript(script)
            await db.commit()

# Global db manager
db_manager = SQLiteManager()

# Convenience functions
async def execute(query: str, *args) -> None:
    return await db_manager.execute(query, *args)

async def fetch_one(query: str, *args) -> Optional[aiosqlite.Row]:
    return await db_manager.fetch_one(query, *args)

async def fetch_many(query: str, *args) -> List[aiosqlite.Row]:
    return await db_manager.fetch_many(query, *args)

async def execute_many(query: str, args_list: List[tuple]) -> None:
    return await db_manager.execute_many(query, args_list)
