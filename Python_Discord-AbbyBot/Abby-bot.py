# Secret Token
from dotenv import load_dotenv
load_dotenv()

# Imports
import os
import discord
from discord.ext import commands

# Bot_token in .env

token = os.getenv("BOT_TOKEN")

# Cog command import

from chat_commands.RockPaperScissors import RockPaperScissors
from chat_commands.Ping import Ping
from chat_commands.Code import Code
from chat_commands.Help import Help


# Events import

from event_codes.Deleted_messages import Deleted_Messages
from event_codes.Abby_mentions import Abby_mentions

# Bot prefix
bot = commands.Bot(command_prefix='abbybot_', intents=discord.Intents.all())

@bot.event # Load all extra script python files
async def on_ready():
    print(f'Bot started as {bot.user.name}')

    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="Bocchi the Rock!", 
    ))
    
    await bot.add_cog(Ping(bot))
    await bot.add_cog(RockPaperScissors(bot))
    await bot.add_cog(Code(bot))
    
   # await bot.add_cog(ObtenerAcceso(bot))
    await bot.add_cog(Deleted_Messages(bot))
    await bot.add_cog(Abby_mentions(bot))
    await bot.add_cog(Help(bot))

    await bot.tree.sync()  # Synchronize slash commands globally


    print("Synchronized slash commands.")

try:
    bot.run(token)  # Token run
except Exception as e:
    print(f"An error has occurred: {e}") 


