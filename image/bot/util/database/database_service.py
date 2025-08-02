
from .database_models import ServerModel, UserModel, ChannelModel, MessageModel, LogModel
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """High-level database operations for Discord bot"""

    @staticmethod
    async def initialize_discord_entities(bot):
        """Initialize database with current Discord entities"""
        try:
            for guild in bot.guilds:
                await ServerModel.insert_or_update(
                    server_id=guild.id,
                    server_name=guild.name,
                    region=str(guild.region) if hasattr(guild, 'region') else None
                )

                # Insert channels
                for channel in guild.channels:
                    channel_type = 'text' if hasattr(channel, 'send') else 'voice'
                    await ChannelModel.insert_or_update(
                        channel_id=channel.id,
                        server_id=guild.id,
                        channel_name=channel.name,
                        channel_type=channel_type
                    )

                # Insert members
                for member in guild.members:
                    await UserModel.insert_or_update(
                        user_id=member.id,
                        username=member.name,
                        display_name=member.display_name
                    )

            logger.info("Database initialized with current Discord entities")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    @staticmethod
    async def log_discord_event(level: str, event_type: str, message: str, **context):
        """Centralized Discord event logging"""
        await LogModel.insert_discord_log(
            level=level,
            event_type=event_type,
            message=message,
            **context
        )

# Convenience functions for backward compatibility
async def insert_server(server_id: int, server_name: str, region: str = None):
    return await ServerModel.insert_or_update(server_id, server_name, region)

async def insert_user(user_id: int, username: str, display_name: str = None):
    return await UserModel.insert_or_update(user_id, username, display_name)

async def insert_channel(channel_id: int, server_id: int = None, channel_name: str = None, channel_type: str = 'text'):
    return await ChannelModel.insert_or_update(channel_id, server_id, channel_name, channel_type)

async def insert_message(channel_id: int, user_id: int, content: str, discord_message_id: int = None):
    return await MessageModel.insert(channel_id, user_id, content, discord_message_id)

async def insert_discord_log(level: str, event_type: str, message: str, logger_name: str = "discord", **kwargs):
    return await LogModel.insert_discord_log(level, event_type, message, logger_name, **kwargs)

async def get_server_stats(server_id: int):
    return await ServerModel.get_stats(server_id)

async def get_recent_logs(limit: int = 100, event_type: str = None, level: str = None):
    return await LogModel.get_recent_logs(limit, event_type, level)

async def get_discord_logs(limit: int = 100, server_id: int = None):
    return await LogModel.get_discord_logs(limit, server_id)