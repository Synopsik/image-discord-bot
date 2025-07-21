from discord.ext import commands
from util import api_utils


class GeneralCog(commands.Cog, name="General"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.debug("Loaded General Cog")
        
        
    @commands.command(name="ping")
    async def ping(self, ctx, msg: str | None = None):
        if msg:
            self.logger.debug(f"Pong!")
            await ctx.send(f"Pong!\n{msg}")
        else:
            self.logger.debug(f"Pong!")
            await ctx.send("Pong!")    
        
        
    @commands.command(name="health")
    async def health_check(self, ctx, verbosity = 1):
        response = await api_utils.health_get(
            verbosity=int(verbosity), 
            logger=self.logger
        )
        await ctx.send(response["health"])


async def setup(bot):
    await bot.add_cog(GeneralCog(bot, bot.logger))

