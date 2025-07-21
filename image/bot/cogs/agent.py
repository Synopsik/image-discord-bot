import os
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands

from util.api_utils import query_post, models_get
from util.message_utils import send_message

class AgentCog(commands.Cog, name="Agent"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.debug("Loaded Agent Cog")
        
    
    @commands.command(name="query")
    async def query_agent(self, ctx, *msg):
        """
        Handles the query command to process user input and respond with the
        message or inform the user if no message is provided.

        :param ctx: The context of the command invocation, typically includes
                    information about its usage and the channel.
        :param msg: A tuple containing parts of the message passed with the
                    command. This is processed and joined into a single string.
        :return: None, as the function sends messages directly to the context.
        """
        try:
            if msg:
                msg = " ".join(msg) # Convert msg tuple to single string, delimits words using spaces 
                self.logger.debug(f"Queried Agent: {self.bot.llm} ({self.bot.model})")
                async with ctx.typing():
                    response = await query_post(
                        prompt=msg,
                        llm=self.bot.llm,
                        model=self.bot.model,
                        logger=self.logger
                    )
                    self.logger.debug(response)
                    await send_message(ctx=ctx, message=response, logger=self.logger) # Send the converted message
            else:
                self.logger.debug(f"Didnt enter a message")
                await ctx.send("Enter a message")
        except Exception as e:
            self.logger.error(e)
        
            
    @commands.command(name="models")
    async def get_models(self, ctx, *model):
        models = await models_get(self.logger)
        try:
            async with ctx.typing():
                await ctx.send(f"**Current AI**\n"
                               f"*Bot:* {self.bot.llm}\n"
                               f"*Model:* {self.bot.model}\n\n"
                               f"*Models List:*\n"
                               f"{models}")
        except Exception as e:
            self.logger.error(f"Agent Cog::get_models:: {e}")
        if model:
            pass # TODO Implement changing models
    
async def setup(bot):
    await bot.add_cog(AgentCog(bot, bot.logger))