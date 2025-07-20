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
        """
        Flips a coin and sends the result as a message. The outcome is randomly chosen between 
        "Heads" and "Tails". The result is also logged for records.

        :param ctx: The context in which the command is invoked. This is used to send a response 
            back to the user.
        :return: None
        """
        result = random.choice(["Heads", "Tails"])
        await ctx.send(f"The coin landed on **{result}**")
        self.logger.info(f"The coin landed on {result}")


    @commands.command(name="rps")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rps(self, ctx, choice: str):
        """
        Handles a game of rock-paper-scissors between the user and the bot. The bot randomly
        selects an option, and the game determines the winner based on the player's and the bot's
        choices.

        :param ctx: The command context provided by Discord, representing the state of the command.
        :type ctx: commands.Context
        :param choice: The player's choice of "rock", "paper", or "scissors".
        :type choice: str
        :return: None. Sends a message to the Discord channel with the result of the game.
        :rtype: None
        """
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