import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from cogwatch import watch

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

from util.database.database_utils import db_manager, setup_database
from util.logging_utils import setup_logging, get_db_handler


logger = logging.getLogger("DiscordBot")

class DiscordBot(commands.Bot):
    def __init__(self):
        self.logger_name = "Discord Logger"
        self.prefix = "/"
        self.description = "A Discord bot that has multipurpose utility"
        self.llm = "ollama"
        self.model = "deepseek-r1:7b"
        self.guild_id = os.getenv("GUILD_ID")
        
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
        try:
            await setup_database()
            logger.info("Database setup completed")
            
            setup_logging(db_manager, logging.DEBUG)
            logger.info("Logging configuration completed")
        except Exception as e:
            logger.error(f"Failed to configure bot: {e}")
            raise
            
            
    @watch(path='cogs', preload=True)
    async def on_ready(self):
        logger.debug(f"Logged in as {self.user} (ID: {self.user.id})")
        
    async def close(self):
        logger.info("Shutting down bot...")
        
        db_handler = get_db_handler()
        if db_handler:
            await db_handler.async_close()
            
        logger.info("Bot connection closed")
        await super().close()

if __name__ == "__main__":
    DiscordBot()