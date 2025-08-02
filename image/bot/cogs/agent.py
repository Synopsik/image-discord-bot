import os
import logging
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands

from util.api_utils import query_post, models_get
from util.message_utils import send_message, parse_args

logger = logging.getLogger(__name__)

class AgentCog(commands.Cog, name="Agent"):
    def __init__(self, bot):
        self.bot = bot
        
    
        
    @commands.Cog.listener()
    async def on_ready(self):
        logger.debug("Loaded Agent Cog")
        
    
    @commands.command(name="query")
    async def query(self, ctx, *msg):
        # Need to add attachment handling image, audio, text, etc
        try:
            if msg:
                msg = " ".join(msg) # Convert msg tuple to single string, delimits words using spaces 
                logger.debug(f"Queried Agent: {self.bot.llm} ({self.bot.model})")
                async with ctx.typing():
                    response = await query_post(
                        prompt=msg,
                        llm=self.bot.llm,
                        model=self.bot.model,
                    )
                    logger.debug(response)
                    await send_message(ctx=ctx, message=response) # Send the converted message
            else:
                logger.debug(f"Didnt enter a message")
                await ctx.send("Enter a query")
        except Exception as e:
            logger.error(e)
        
            
    @commands.command(name="model")
    async def model(self, ctx, *args):
        
        logger.debug(f"Models arguments: {args}")
        models = await models_get(logger)
        
        if args:
            content = " ".join(args)
            
            async with ctx.typing():
                parsed = await parse_args(content)
                
                try:
                    if parsed["llm"] and parsed["model"]:
                        if parsed["model"] in models: 
                            logger.debug(f"Parsed model: {parsed["model"]}")
                            self.bot.llm = parsed["llm"]
                            self.bot.model = parsed["model"]
                            
                            await ctx.send(f'**UPDATED**\n'
                                           f'llm: {parsed["llm"]}\n'
                                           f'model: {parsed["model"]}')
                        else:
                            raise Exception
                    else:
                        raise Exception
                except Exception as e:
                    await ctx.send("Error: Use `llm=` and `model=`")
        else:
            try:
                async with ctx.typing():
                    ollama_models = "\n".join([f'model={model}' for model in models]) # in models["ollama"]
                    
                    # It would be better to refactor this so that we loop through 
                    # available LLMs and use a template to print each
                    await ctx.send(f"__***Current AI***__\n"
                                   f"*LLM:* {self.bot.llm}\n"
                                   f"*Model:* {self.bot.model}\n\n"
                                   f"__**USAGE**__\n"
                                   f"`/model llm=ollama model=deepseek-r1:7b`\n\n"
                                   f"__**Ollama**__\n"
                                   f"`llm=ollama`\n"
                                   f"**Models:**\n"
                                   f"`{ollama_models}`\n\n" 
                                   f"__**Bedrock (AWS)**__\n"
                                   f"`llm=bedrock`\n"
                                   f"")
            except Exception as e:
                logger.error(f"Agent Cog::get_models:: {e}")
        
async def setup(bot):
    await bot.add_cog(AgentCog(bot))