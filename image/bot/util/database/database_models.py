from .database_utils import db_manager
from datetime import datetime
from typing import Optional, List

class ServerModel:
    @staticmethod
    async def insert_or_update(server_id: int, server_name: str, region: str = None):
        await db_manager.execute("""
            INSERT INTO Servers (server_id, server_name, region, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(server_id) DO UPDATE SET
                server_name = excluded.server_name,
                region = excluded.region
            """,
            server_id, server_name, region
        )
        
    @staticmethod
    async def get_stats(server_id: int):
        return await db_manager.fetch_one("""
    SELECT s.server_name,
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
    
class UserModel:
    @staticmethod
    async def insert_or_update(user_id: int, username: str, display_name: str = None):
        await db_manager.execute("""
            INSERT INTO Users (user_id, username, display_name, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                display_name = excluded.display_name
             """,
            user_id, username, display_name
        )
        
class ChannelModel:
    @staticmethod
    async def insert_or_update(channel_id: int, server_id: int = None, 
                               channel_name: str = None, channel_type: str = 'text'):
        await db_manager.execute("""
            INSERT INTO Channels (channel_id, server_id, channel_name, channel_type, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(channel_id) DO UPDATE SET
                server_id = excluded.server_id,
                channel_name = excluded.channel_name,
                channel_type = excluded.channel_type""",
            channel_id, server_id, channel_name, channel_type
        )
    
class MessageModel:
    @staticmethod
    async def insert(channel_id: int, user_id: int, content: str, discord_message_id: int = None):
        await db_manager.execute("""
            INSERT INTO Messages (discord_message_id, channel_id, user_id, content, sent_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            discord_message_id, channel_id, user_id, content
        )
        
class LogModel:
    @staticmethod
    async def insert_discord_log(level: str, event_type: str, message: str,
                                 logger_name: str = "discord", server_id: int = None,
                                 user_id: int = None, channel_id: int = None,
                                 extra_data: str = None):
        await db_manager.execute("""
            INSERT INTO Logs (timestamp, level, logger_name, event_type, message,
                                server_id, user_id, channel_id, extra_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            datetime.now().isoformat(), level, logger_name, event_type, message,
            server_id, user_id, channel_id, extra_data
        )
        
    @staticmethod
    async def insert_app_log(level: str, logger_name: str, message: str,
                             module: str = None, function_name: str = None,
                             line_number: int = None, extra_data: str = None):
        await db_manager.execute("""
            INSERT INTO Logs (timestamp, level, logger_name, event_type, message,
                                module, function_name, line_number, extra_data)
            VALUES (?, ?, ?, 'app_log', ?, ?, ?, ?, ?)
            """,
            datetime.now().isoformat(), level, logger_name, message,
            module, function_name, line_number, extra_data

        )
        
    @staticmethod
    async def get_recent_logs(limit: int = 100, event_type: str = None, level: str = None):
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

    @staticmethod
    async def get_discord_logs(limit: int = 100, server_id: int = None):
        if server_id:
            return await db_manager.fetch_many("""
                SELECT l.*, s.server_name, u.username, c.channel_name
                FROM Logs l
                LEFT JOIN Servers s ON l.server_id = s.server_id
                LEFT JOIN Users u ON l.user_id = u.user_id
                LEFT JOIN Channels c ON l.channel_id = c.channel_id
                WHERE l.event_type LIKE 'discord_%' AND l.server_id = ?
                ORDER BY l.created_at DESC LIMIT ?
                """,
                server_id, limit
            )
        else:
            return await db_manager.fetch_many("""
                SELECT l.*, s.server_name, u.username, c.channel_name
                FROM Logs l
                LEFT JOIN Servers s ON l.server_id = s.server_id
                LEFT JOIN Users u ON l.user_id = u.user_id
                LEFT JOIN Channels c ON l.channel_id = c.channel_id
                WHERE l.event_type LIKE 'discord_%'
                ORDER BY l.created_at DESC LIMIT ?
                """,
                limit

            )
        
    @staticmethod
    async def cleanup_old_logs(days_to_keep: int = 30):
        await db_manager.execute(
            "DELETE FROM Logs WHERE created_at < datetime('now', '-' || ? || ' days')",
            days_to_keep
        )