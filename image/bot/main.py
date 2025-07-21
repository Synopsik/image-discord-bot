import os
import logging
import asyncio
import asyncpg
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from cogwatch import watch

load_dotenv()

from util.logging_utils import setup_logging
from cogs.agent import AgentCog
from cogs.logging import LoggingCog
from cogs.general import GeneralCog
from cogs.games import GamesCog
from cogs.admin import AdminCog

class DiscordBot(commands.Bot):
    def __init__(self, *cogs):
        self.db_pool = None
        self.logger = None
        self.cogs_list = cogs
        self.logger_name = "Discord Logger"
        self.prefix = "/"
        self.description = "A Discord bot that has multipurpose utility"
        self.llm = "ollama"
        self.model = "deepseek-r1:7b"
        
        # intents config
        intents = discord.Intents.default()
        intents.presences = True
        intents.members = True
        intents.message_content = True
        
        super().__init__(
            command_prefix=self.prefix,
            intents=intents,
            description=self.description
        )
        
        self.run(os.getenv("BOT_TOKEN"))
        
    async def setup_hook(self):
        # Need to create an implementation for AWS DynamoDB to hold Discord logs
        try:
            loop = asyncio.get_running_loop()
            self.logger = setup_logging(self.db_pool, loop, self.logger_name, logging.DEBUG, "logs")
        except Exception as e:
            print(f"Failed to configure logger. Error: {e}")
            
            
    @watch(path='cogs', preload=True)
    async def on_ready(self):
        guild_id = os.getenv("GUILD_ID")
        if guild_id:
            await self.tree.sync(guild=discord.Object(id=int(guild_id))) # This seems like it isn't working
            self.logger.debug(f"Synced Tree Commands with guild: {guild_id}")
        else:
            await self.tree.sync()
            self.logger.debug("Synced Tree Commands without guild")
        self.logger.debug(f"Logged in as {self.user} (ID: {self.user.id})")
        
    async def close(self):
        if self.db_pool is not None:
            if hasattr(self, "db_pool"):
                self.logger.debug("Close database connection")
                await self.db_pool.close()
        self.logger.debug("Close bot connection")
        await super().close()

if __name__ == "__main__":
    DiscordBot(
        "agent",
        "logging",
        "general",
        "games",
        "admin"
    )