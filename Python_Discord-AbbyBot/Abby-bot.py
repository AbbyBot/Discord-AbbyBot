# Imports
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import mysql.connector

import sys
import schedule
import time
import threading

# Load dotenv variables
load_dotenv()

# Bot_token  .env
token = os.getenv("BOT_TOKEN")

# MySQL connection
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor()

# Cog command import
from chat_commands.RockPaperScissors import RockPaperScissors
from chat_commands.Ping import Ping
from chat_commands.Code import Code
from chat_commands.Help import Help
from chat_commands.Set_language import SetLanguage
from chat_commands.TellHistory import TellHistory

# Events import
from event_codes.Deleted_messages import Deleted_Messages
from event_codes.Abby_mentions import Abby_mentions

# Bot Prefix default
bot = commands.Bot(command_prefix='abbybot_', intents=discord.Intents.all())

# Function to restart the bot
def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)  # Reinicia el script de Python actual
    print("Bot is restarting...")

# Scheduler to restart the bot every hour
def schedule_restart():
    schedule.every(2).hours.do(restart_bot)

    while True:
        schedule.run_pending()
        time.sleep(1)


# Function to register new servers
def register_server(guild):
    # Query the default language ID (in this case 'en' for English)
    cursor.execute("SELECT id FROM languages WHERE language_code = %s", ('en',))
    default_language_id = cursor.fetchone()[0]  #get the language ID

    # check if the server is already registered
    cursor.execute("SELECT guild_id FROM server_settings WHERE guild_id = %s", (guild.id,))
    result = cursor.fetchone()

    if result is None:
        # If the server is not registered, we add it with the default language
        cursor.execute("INSERT INTO server_settings (guild_id, guild_name, owner_id, member_count, prefix, guild_language) VALUES (%s, %s, %s, %s, %s, %s)",
                       (guild.id, guild.name, guild.owner_id, guild.member_count, 'abbybot_', default_language_id))
        db.commit()
        print(f"Server {guild.name} registered with default language in English (ID: {default_language_id}).")
    else:
        print(f"Server {guild.name} is already registered.")


@bot.event
async def on_ready():
    print(f'Bot started as {bot.user.name}')

    # Start the scheduler in a separate thread

    
   # Uncomment this line when deployed in production 
   #  threading.Thread(target=schedule_restart).start()
    
    # Register servers where the bot is already present
    for guild in bot.guilds:
        register_server(guild)
    
    # Change bot presence
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="Bocchi the Rock!", 
    ))

    # Load cogs slash commands (cogs)
    await bot.add_cog(Ping(bot))
    await bot.add_cog(RockPaperScissors(bot))
    await bot.add_cog(Code(bot))
    await bot.add_cog(Deleted_Messages(bot))
    await bot.add_cog(Abby_mentions(bot))
    await bot.add_cog(Help(bot))
    await bot.add_cog(SetLanguage(bot))
    await bot.add_cog(TellHistory(bot))
    
    # Sync slash commands globally or to specific guilds
    try:
        synced_commands = await bot.tree.sync()
        print(f"Successfully synced {len(synced_commands)} commands.")
    except Exception as e:
        print(f"An error occurred while syncing commands: {e}")


@bot.event
async def on_guild_join(guild):
    # Register the server when the bot is added to a new server
    register_server(guild)
    print(f"Joined and registered new server: {guild.name}")

# Close the connection to the database when the bot ends
@bot.event
async def on_close():
    cursor.close()
    db.close()
    print("Database connection closed.")

try:
    bot.run(token)  # Token run
except Exception as e:
    print(f"An error has occurred: {e}") 
