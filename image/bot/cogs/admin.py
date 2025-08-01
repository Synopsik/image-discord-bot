import discord
from discord.ext import commands
import logging
logger = logging.getLogger(__name__)


class AdminCog(commands.Cog, name="Admin"):
    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        logger.debug("Loaded Admin Cog")
        
        
        
    @commands.command(name="clear")
    @commands.is_owner()
    async def clear_chat(self, ctx, remove:int=None):
        async with ctx.typing():
            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.channel.purge(limit=remove)
            else:
                count = 0
                async for message in ctx.channel.history(limit=remove):
                    if message.author == self.bot.user:
                        await message.delete()
                        count+=1
                await ctx.send(f"Deleted {count} of my messages")
                logger.info(f"Deleted {count} of my messages")


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
