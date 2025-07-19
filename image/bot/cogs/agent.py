import os
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands

from util.api_utils import query

class AgentCog(commands.Cog, name="Agent"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.debug("Loaded Agent Cog")
        
    
    @commands.command(name="query")
    async def query_agent(self, ctx, msg: str | None = None):
        if msg:
            self.logger.debug(f"Queried Agent: {msg}")
            await ctx.send(msg)
        else:
            self.logger.debug(f"Didnt enter a message")
            await ctx.send("Enter a message")

        
        
                