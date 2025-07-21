import random
from discord.ext import commands
from cogs.logging import get_formatted_time

class GamesCog(commands.Cog, name="Games"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.debug("Loaded Games Cog")


    @commands.command(name="coinflip")
    async def coinflip(self, ctx):
        result = random.choice(["Heads", "Tails"])
        await ctx.send(f"The coin landed on **{result}**")
        self.logger.info(f"The coin landed on {result}")


    @commands.command(name="rps")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rps(self, ctx, choice: str):
        options = ["rock", "paper", "scissors"]
        choice = choice.lower()
        if choice not in options:
            await ctx.send("Please choose 'rock', 'paper', or 'scissors'.")
            return
        bot_choice = random.choice(options)
        # Determine winrar
        if choice == bot_choice:
            outcome = "It's a tie!"
        elif (
                (choice == "rock" and bot_choice == "scissors") or
                (choice == "paper" and bot_choice == "rock") or
                (choice == "scissors" and bot_choice == "paper")
        ):
            outcome = "You won!"
        else:
            outcome = "I win!"
        await ctx.send(f"You chose **{choice}**, I chose **{bot_choice}**. {outcome}")
        self.logger.info(f"{ctx.author} chose {choice}, I chose {bot_choice}. {outcome}")


async def setup(bot):
    await bot.add_cog(GamesCog(bot, bot.logger))
