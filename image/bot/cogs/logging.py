import datetime
from discord.ext import commands


async def get_formatted_time():
    dt = datetime.datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

class LoggingCog(commands.Cog, name="Logging"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.debug("Loaded Log Cog")

    # ----------------------------------------------------------------------------
    # Messages
    # ----------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author == self.bot.user:
            self.logger.info(f"{message.author}: {message.content}")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.logger.warning(f"{message.author.name} has deleted a message: {message.content}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        self.logger.warning(f"{before.author.name} has edited a message: {before.content} -> {after.content}")


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        self.logger.debug(f"{user.name} has added a reaction to a message: {reaction.emoji}")

    # ----------------------------------------------------------------------------
    # Members
    # ----------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.logger.debug(f"{member.name} just joined the server!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.logger.warning(f"{member.name} just left the server!")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        self.logger.warning(f"{before.name} has changed their nickname to {after.name}")

    # ----------------------------------------------------------------------------
    # Commands
    # ----------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.logger.debug(f"Command completed: {ctx.prefix}{ctx.command}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        self.logger.error(f"Command error: {ctx.prefix}{error}")