import asyncio
import logging
import os.path
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

import aiosqlite

logger = logging.getLogger(__name__) # Probably want to change this?


DATABASE_SCHEMA = """
-- Initially, drop any existing tables (reverse order due to foreign keys)
DROP TABLE IF EXISTS ApplicationLogs;
DROP TABLE IF EXISTS Logs;
DROP TABLE IF EXISTS Messages;
DROP TABLE IF EXISTS Channels;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Servers;

-- Servers table
CREATE TABLE Servers (
    server_id   INTEGER       NOT NULL PRIMARY KEY, -- Discord server IDs are big integers
    server_name TEXT          NOT NULL,
    region      TEXT          NULL,
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE Users (
    user_id      INTEGER       NOT NULL PRIMARY KEY, -- Discord user IDs are big integers
    username     TEXT          NOT NULL,
    display_name TEXT          NULL,
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Channels table
CREATE TABLE Channels (
    channel_id   INTEGER       NOT NULL PRIMARY KEY, -- Discord channel IDs are big integers
    server_id    INTEGER       NULL,
    channel_name TEXT          NULL,
    channel_type TEXT          NOT NULL CHECK (channel_type IN ('text','voice','DM')),
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(server_id) REFERENCES Servers(server_id) ON DELETE CASCADE
);

-- Create index for server_id in Channels
CREATE INDEX IX_Channels_Server ON Channels(server_id);

-- Messages table
CREATE TABLE Messages (
    message_id   INTEGER       PRIMARY KEY AUTOINCREMENT, -- Auto-incrementing primary key
    discord_message_id INTEGER NULL, -- Actual Discord message ID (optional)
    channel_id   INTEGER       NOT NULL,
    user_id      INTEGER       NOT NULL,
    content      TEXT          NOT NULL,
    sent_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(channel_id) REFERENCES Channels(channel_id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Create indexes for Messages
CREATE INDEX IX_Messages_Channel ON Messages(channel_id);
CREATE INDEX IX_Messages_User ON Messages(user_id);
CREATE INDEX IX_Messages_Discord ON Messages(discord_message_id);

-- Unified Logs table (handles both Discord events AND application logging)
CREATE TABLE Logs (
    log_id        INTEGER       PRIMARY KEY AUTOINCREMENT,
    timestamp     TEXT          NOT NULL, -- ISO format timestamp
    level         TEXT          NOT NULL, -- INFO, DEBUG, WARNING, ERROR, CRITICAL
    logger_name   TEXT          NOT NULL, -- Source logger name
    event_type    TEXT          NOT NULL, -- 'discord_event', 'app_log', 'command', 'error', etc.
    message       TEXT          NOT NULL, -- Log message/description
    -- Discord-specific fields
    server_id     INTEGER       NULL,
    user_id       INTEGER       NULL,
    channel_id    INTEGER       NULL,
    -- Application-specific fields
    module        TEXT          NULL,
    function_name TEXT          NULL,
    line_number   INTEGER       NULL,
    extra_data    TEXT          NULL,     -- JSON data for additional context
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(channel_id) REFERENCES Channels(channel_id) ON DELETE SET NULL,
    FOREIGN KEY(server_id) REFERENCES Servers(server_id) ON DELETE SET NULL,
FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE SET NULL
);

-- Create indexes for Logs
CREATE INDEX IX_Logs_Level ON Logs(level);
CREATE INDEX IX_Logs_EventType ON Logs(event_type);
CREATE INDEX IX_Logs_Logger ON Logs(logger_name);
CREATE INDEX IX_Logs_Timestamp ON Logs(timestamp DESC);
CREATE INDEX IX_Logs_ServerUser ON Logs(server_id, user_id);
CREATE INDEX IX_Logs_CreatedAt ON Logs(created_at DESC);
"""


class SQLiteManager:
    def __init__(self, db_path: str=None):
        if db_path is None:
            # Get the dir where this file is
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Define and create directory "data" relative to this file
            db_dir = os.path.join(current_dir, "data")
            os.makedirs(db_dir, exist_ok=True)
            self.db_path = os.path.join(db_dir, "logs.db") # Database name
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
            
    async def setup_database(self):
        """Setup SQLite database with Discord schema"""
        try:
            logger.info("Setting up database schema...")
            await self.execute_script(DATABASE_SCHEMA)
            logger.info("Database schema setup complete")
        
            tables = await self.verify_tables()
            logger.info(f"Created tables: {', '.join(tables)}")
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise

    async def verify_tables(self):
        """Verify that all expected tables are created"""
        expected_tables = ['Servers', 'Users', 'Channels', 'Messages', 'Logs']
        
        result = await self.fetch_many(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        
        created_tables = [row['name'] for row in result]
        missing_tables = set(expected_tables) - set(created_tables)
        
        if missing_tables:
            logger.warning(f"Missing tables: {', '.join(missing_tables)}")
        
        return created_tables
        
        

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

async def setup_database():
    await db_manager.setup_database()