import logging
from util.database_utils import db_manager

logger = logging.getLogger(__name__)

# SQLite schema - unified logging approach
database_setup_script = """
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
CREATE INDEX IX_Logs_CreatedAt ON Logs(created_at DESC); \
"""

async def setup_database():
    """Setup SQLite database with Discord-specific schema"""
    try:
        logger.info("Setting up database schema...")
        await db_manager.execute_script(database_setup_script)
        logger.info("✓ Database schema setup completed successfully!")

        # Verify tables were created
        tables = await verify_tables()
        logger.info(f"✓ Created tables: {', '.join(tables)}")

    except Exception as e:
        logger.error(f"✗ Database setup failed: {e}")
        raise

async def verify_tables():
    """Verify that all expected tables were created"""
    expected_tables = ['Servers', 'Users', 'Channels', 'Messages', 'Logs']

    # Query SQLite system table to get list of tables
    result = await db_manager.fetch_many(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )

    created_tables = [row['name'] for row in result]

    # Check if all expected tables exist
    missing_tables = set(expected_tables) - set(created_tables)
    if missing_tables:
        logger.warning(f"Missing tables: {', '.join(missing_tables)}")

    return created_tables

# Helper functions for database operations
async def insert_server(server_id: int, server_name: str, region: str = None):
    """Insert or update server information"""
    await db_manager.execute(
        """
        INSERT INTO Servers (server_id, server_name, region, created_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(server_id) DO UPDATE SET
            server_name = excluded.server_name,
            region = excluded.region
        """,
        server_id, server_name, region
    )

async def insert_user(user_id: int, username: str, display_name: str = None):
    """Insert or update user information"""
    await db_manager.execute(
        """
        INSERT INTO Users (user_id, username, display_name, created_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            display_name = excluded.display_name

        """,
        user_id, username, display_name
    )

async def insert_channel(channel_id: int, server_id: int = None, channel_name: str = None, channel_type: str = 'text'):
    """Insert or update channel information"""
    await db_manager.execute(
        """
        INSERT INTO Channels (channel_id, server_id, channel_name, channel_type, created_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(channel_id) DO UPDATE SET
            server_id = excluded.server_id,
            channel_name = excluded.channel_name,
            channel_type = excluded.channel_type
        """,
        channel_id, server_id, channel_name, channel_type
    )

async def insert_message(channel_id: int, user_id: int, content: str, discord_message_id: int = None):
    """Insert a new message"""
    await db_manager.execute(
        """
        INSERT INTO Messages (discord_message_id, channel_id, user_id, content, sent_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        discord_message_id, channel_id, user_id, content
    )

# Unified logging functions
async def insert_discord_log(level: str, event_type: str, message: str, logger_name: str = "discord",
                             server_id: int = None, user_id: int = None, channel_id: int = None,
                             extra_data: str = None):
    """Insert a Discord event log"""
    from datetime import datetime
    await db_manager.execute(
        """
        INSERT INTO Logs (timestamp, level, logger_name, event_type, message,
                          server_id, user_id, channel_id, extra_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        datetime.now().isoformat(), level, logger_name, event_type, message,
        server_id, user_id, channel_id, extra_data
    )

async def insert_app_log(level: str, logger_name: str, message: str, module: str = None,
                         function_name: str = None, line_number: int = None, extra_data: str = None):
    """Insert an application log"""
    from datetime import datetime
    await db_manager.execute(
        """
        INSERT INTO Logs (timestamp, level, logger_name, event_type, message,
                          module, function_name, line_number, extra_data)
        VALUES (?, ?, ?, 'app_log', ?, ?, ?, ?, ?)
        """,
        datetime.now().isoformat(), level, logger_name, message,
        module, function_name, line_number, extra_data
    )

# Query helper functions
async def get_server_stats(server_id: int):
    """Get statistics for a server"""
    return await db_manager.fetch_one(
        """
        SELECT
            s.server_name,
            COUNT(DISTINCT c.channel_id) as channel_count,
            COUNT(DISTINCT u.user_id) as user_count,
            COUNT(m.message_id) as message_count
        FROM Servers s
                 LEFT JOIN Channels c ON s.server_id = c.server_id
                 LEFT JOIN Messages m ON c.channel_id = m.channel_id
                 LEFT JOIN Users u ON m.user_id = u.user_id
        WHERE s.server_id = ?
        GROUP BY s.server_id, s.server_name
        """,
        server_id
    )

async def get_recent_logs(limit: int = 100, event_type: str = None, level: str = None):
    """Get recent log entries with optional filtering"""
    base_query = """
                 SELECT l.*, s.server_name, u.username, c.channel_name
                 FROM Logs l
                          LEFT JOIN Servers s ON l.server_id = s.server_id
                          LEFT JOIN Users u ON l.user_id = u.user_id
                          LEFT JOIN Channels c ON l.channel_id = c.channel_id \
                 """

    conditions = []
    params = []

    if event_type:
        conditions.append("l.event_type = ?")
        params.append(event_type)

    if level:
        conditions.append("l.level = ?")
        params.append(level)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY l.created_at DESC LIMIT ?"
    params.append(limit)

    return await db_manager.fetch_many(base_query, *params)

async def get_discord_logs(limit: int = 100, server_id: int = None):
    """Get Discord-specific logs"""
    if server_id:
        return await db_manager.fetch_many(
            """
            SELECT l.*, s.server_name, u.username, c.channel_name
            FROM Logs l
                     LEFT JOIN Servers s ON l.server_id = s.server_id
                     LEFT JOIN Users u ON l.user_id = u.user_id
                     LEFT JOIN Channels c ON l.channel_id = c.channel_id
            WHERE l.event_type LIKE 'discord_%' AND l.server_id = ?
            ORDER BY l.created_at DESC
                LIMIT ?
            """,
            server_id, limit
        )
    else:
        return await db_manager.fetch_many(
            """
            SELECT l.*, s.server_name, u.username, c.channel_name
            FROM Logs l
                     LEFT JOIN Servers s ON l.server_id = s.server_id
                     LEFT JOIN Users u ON l.user_id = u.user_id
                     LEFT JOIN Channels c ON l.channel_id = c.channel_id
            WHERE l.event_type LIKE 'discord_%'
            ORDER BY l.created_at DESC
                LIMIT ?
            """,
            limit
        )

async def get_app_logs(limit: int = 100, level: str = None):
    """Get application logs"""
    if level:
        return await db_manager.fetch_many(
            """
            SELECT * FROM Logs
            WHERE event_type = 'app_log' AND level = ?
            ORDER BY created_at DESC
                LIMIT ?
            """,
            level, limit
        )
    else:
        return await db_manager.fetch_many(
            """
            SELECT * FROM Logs
            WHERE event_type = 'app_log'
            ORDER BY created_at DESC
                LIMIT ?
            """,
            limit
        )

async def cleanup_old_logs(days_to_keep: int = 30):
    """Clean up old log entries"""
    result = await db_manager.execute(
        "DELETE FROM Logs WHERE created_at < datetime('now', '-' || ? || ' days')",
        days_to_keep
    )
    logger.info(f"Cleaned up logs older than {days_to_keep} days")
    return result