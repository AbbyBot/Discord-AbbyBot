import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rockpaperscissors", description="Choose between rock, paper or scissors to play.")    

    @app_commands.choices(option=[
        discord.app_commands.Choice(name="Rock", value=1),
        discord.app_commands.Choice(name="Paper", value=2),
        discord.app_commands.Choice(name="Scissors", value=3),
    ])

    async def rockpaperscissors(self, interaction: discord.Interaction, option: int):
        if option == 1:
            user_choice = "rock"
            await interaction.response.send_message(f"You choose {user_choice.capitalize()}.")
        elif option == 2:
            user_choice = "paper"
            await interaction.response.send_message(f"You choose {user_choice.capitalize()}.")
        else:
            user_choice = "scissors"
            await interaction.response.send_message(f"You choose {user_choice.capitalize()}.")

        await asyncio.sleep(1)

        await interaction.channel.send(f"Hmm... I'll choose...")

        await asyncio.sleep(2)  

        bot_numberchoice = random.randint(1,3)

        if bot_numberchoice == 1:
            bot_choice = "rock"
        elif bot_numberchoice == 2:
            bot_choice = "paper"
        else:
            bot_choice = "scissors"

        await interaction.channel.send(f"{bot_choice.capitalize()}.")

        await asyncio.sleep(1)

        if option == 1 and  bot_numberchoice == 3:
            await interaction.channel.send(f"Congratulations! You have chosen  {user_choice.capitalize()} and I {bot_choice.capitalize()}. You won this time.")
        elif option == 2 and bot_numberchoice == 1:
            await interaction.channel.send(f"Congratulations! You have chosen  {user_choice.capitalize()} and I {bot_choice.capitalize()}. You won this time.")
        elif option == 3 and bot_numberchoice == 2:
            await interaction.channel.send(f"Congratulations! You have chosen  {user_choice.capitalize()} and I {bot_choice.capitalize()}. You won this time.")
        elif option == 1 and bot_numberchoice == 2:
            await interaction.channel.send(f"You lose! You have chosen {user_choice.capitalize()} and I {bot_choice.capitalize()}. I have won this time.")
        elif option == 2 and bot_numberchoice == 3:
            await interaction.channel.send(f"You lose! You have chosen {user_choice.capitalize()} and I {bot_choice.capitalize()}. I have won this time.")
        elif option == 3 and bot_numberchoice == 1:
            await interaction.channel.send(f"You lose! You have chosen {user_choice.capitalize()} and I {bot_choice.capitalize()}. I have won this time.")    
        else:
            await interaction.channel.send(f"It's a tie! You have chosen {user_choice.capitalize()} and I {bot_choice.capitalize()}. This time we tied.")      
