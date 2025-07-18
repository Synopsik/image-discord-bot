import os
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands

from image.util.api_utils import query

class AgentCog(commands.Cog, name="Agent"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.debug("Loaded Agent Cog")
        
    
    @app_commands.command(name="query", description="Query the agent")
    async def query_agent(self, interaction: discord.Interaction, query: str):
        self.logger.debug(f"Queried Agent: {query}")
        await interaction.response.send_message(query)

        
        
                