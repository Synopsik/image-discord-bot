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
        """
        Represents a command that responds with "Pong!" when invoked. If an optional
        message is provided, it includes the message in the response.

        :param ctx: Invocation context of the command.
        :type ctx: commands.Context
        :param msg: Optional message to include in the response.
        :type msg: str or None
        :return: None
        """
        if msg:
            self.logger.debug(f"Pong!")
            await ctx.send(f"Pong!\n{msg}")
        else:
            self.logger.debug(f"Pong!")
            await ctx.send("Pong!")    
        
        
    @commands.command(name="health")
    async def health_check(self, ctx, verbosity = 1):
        """
        Checks the health status of the API and sends the result as a response.

        The method performs a health check by reaching out to the external API and retrieves 
        the health status. The amount of information returned is determined by the verbosity 
        level stated when the command is invoked.

        :param ctx: The context in which the command is invoked. This parameter is used 
                    to interact with the Discord API, allowing the bot to send messages 
                    or retrieve additional information based on the invocation context.
        :type ctx: commands.Context
        :param verbosity: The level of detail for the health check. It can vary with the 
                          integer values `1`, `2`, or `3`, where higher values generally 
                          provide more detailed information.
        :type verbosity: int, optional
        :return: None. The result of the health check is sent directly to the context 
                 as a message.
        :rtype: None
        """
        response = await api_utils.health_get(
            verbosity=int(verbosity), 
            logger=self.logger
        )
        await ctx.send(response["health"])
        
