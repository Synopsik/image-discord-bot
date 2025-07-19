import os
import logging
import asyncio
import asyncpg
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

from util.logging_utils import setup_logging
from cogs.agent import AgentCog
from cogs.logging import LoggingCog

class DiscordBot(commands.Bot):
    def __init__(self, *cogs):
        self.db_pool = None
        self.logger = None
        self.cogs_list = cogs
        self.logger_name = "Discord Logger"
        self.prefix = "/"
        self.description = "A Discord bot that has multipurpose utility"
        
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
        
    async def setup_hook(self) -> None:
        # Need to create an implementation for AWS DynamoDB to hold Discord logs
        try:
            loop = asyncio.get_running_loop()
            self.logger = setup_logging(self.db_pool, loop, self.logger_name, logging.DEBUG, "logs")
        except Exception as e:
            print(f"Failed to configure logger. Error: {e}")
            
        try:
            for cog in self.cogs_list:
                match cog:
                    # case "general":
                    #     await self.add_cog(GeneralCog(self, self.logger))
                    # case "games":
                    #     await self.add_cog(GamesCog(self, self.logger))
                    case "logging":
                        await self.add_cog(LoggingCog(self, self.logger))
                    case "agent":
                        await self.add_cog(AgentCog(self, self.logger))
                    case _:
                        # Default case: if no names matches, no cog is added
                        self.logger.error(f"Cog {cog} not found.")
        except Exception as e:
            self.logger.error(f"Couldn't load cog: {e}")
            
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
        "logging"
    )