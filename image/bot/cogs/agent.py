import os
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands

from util.api_utils import query_post, models_get
from util.message_utils import send_message, parse_args


class AgentCog(commands.Cog, name="Agent"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.debug("Loaded Agent Cog")
        
    
    @commands.command(name="query")
    async def query(self, ctx, *msg):
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
        
            
    @commands.command(name="model")
    async def model(self, ctx, *args):
        
        self.logger.debug(f"Models arguments: {args}")
        models = await models_get(self.logger)
        
        if args:
            content = " ".join(args)
            
            async with ctx.typing():
                parsed = await parse_args(content)
                
                try:
                    if parsed["llm"] and parsed["model"]:
                        if parsed["model"] in models: 
                            self.logger.debug(f"Parsed model: {parsed["model"]}")
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
                self.logger.error(f"Agent Cog::get_models:: {e}")
        
async def setup(bot):
    await bot.add_cog(AgentCog(bot, bot.logger))