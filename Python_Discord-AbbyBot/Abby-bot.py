# Imports
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import mysql.connector

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

# Events import
from event_codes.Deleted_messages import Deleted_Messages
from event_codes.Abby_mentions import Abby_mentions

# Bot Prefix default
bot = commands.Bot(command_prefix='abbybot_', intents=discord.Intents.all())

# Function to register new servers
def register_server(guild):
    cursor.execute("SELECT guild_id FROM server_settings WHERE guild_id = %s", (guild.id,))
    result = cursor.fetchone()

    if result is None:
        # If the server is not registered, we add it with default language 'en'
        cursor.execute("INSERT INTO server_settings (guild_id, guild_name, owner_id, member_count, prefix, guild_language) VALUES (%s, %s, %s, %s, %s, %s)",
                       (guild.id, guild.name, guild.owner_id, guild.member_count, 'abbybot_', 'en'))
        db.commit()
        print(f"Server {guild.name} registered with default language in English.")
    else:
        print(f"Server {guild.name} is already registered.")

@bot.event
async def on_ready():
    print(f'Bot started as {bot.user.name}')
    
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
