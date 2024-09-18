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
from chat_commands.TellHistory import TellHistory
from chat_commands.server_info import ServerInfo
from chat_commands.User_info import UserInfo


# settings commands imports
from settings_commands.Set_language import SetLanguage
from settings_commands.Events_control import EventsControl
from settings_commands.set_prefix import SetPrefix
from settings_commands.Set_birthday import SetBirthday


# Events import
from event_codes.Deleted_messages import Deleted_Messages
from event_codes.Abby_mentions import Abby_mentions


# Minigames import
from minigames.blackjack import Blackjack


# APIs commands import
from api_commands.waifu_img import WaifuImg
from api_commands.cat_img import CatImg
from api_commands.neko_img import NekoImg
from api_commands.dog_img import DogImg

# Bot Prefix default
bot = commands.Bot(command_prefix='abbybot_', intents=discord.Intents.all())


# Function to restart the bot
def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)  # Restart Python script
    print("Bot is restarting...")

# Scheduler to restart the bot every hour
def schedule_restart():
    schedule.every(2).hours.do(restart_bot)

    while True:
        schedule.run_pending()
        time.sleep(1)

def ensure_tables_exist():
    tables = ['server_settings', 'dashboard', 'languages', 'mention_counter']  # Add tables to check

    for table in tables:
        cursor.execute(f"SHOW TABLES LIKE '{table}';")
        result = cursor.fetchone()
        if result is None:
            # (Optional) Here you can run the SQL to create the missing tables
            print(f"Table {table} does not exist. You should create it.")
        else:
            print(f"Table {table} already exists.")

# Function to register new servers or update existing servers
def register_server(guild):
    # Query the default language ID (in this case 'en' for English)
    cursor.execute("SELECT id FROM languages WHERE language_code = %s", ('en',))
    default_language_id = cursor.fetchone()[0]

    # Check if the server is already registered
    cursor.execute("SELECT guild_id, guild_name, owner_id, member_count FROM server_settings WHERE guild_id = %s", (guild.id,))
    result = cursor.fetchone()

    if result is None:
        # If the server is not registered, add it with the default language
        cursor.execute("INSERT INTO server_settings (guild_id, guild_name, owner_id, member_count, prefix, guild_language) VALUES (%s, %s, %s, %s, %s, %s)",
                       (guild.id, guild.name, guild.owner.id, guild.member_count, 'abbybot_', default_language_id))
        db.commit()
        print(f"Server {guild.name} registered with default language in English (ID: {default_language_id}).")
    else:
        # Compare the existing values to see if they need updating
        if result[1] != guild.name or result[2] != guild.owner.id or result[3] != guild.member_count:
            cursor.execute("UPDATE server_settings SET guild_name = %s, owner_id = %s, member_count = %s WHERE guild_id = %s",
                           (guild.name, guild.owner.id, guild.member_count, guild.id))
            db.commit()
            print(f"Server {guild.name} updated with new values.")

    # Register or update all members in the dashboard table
    register_members(guild)


def register_members(guild):
    for member in guild.members:
        # Determine if the user is a bot or an administrator
        is_bot = 1 if member.bot else 0  # If it's a bot, is_bot will be 1, otherwise 0
        is_admin = 1 if member.guild_permissions.administrator else 0  # If the user is an admin, is_admin will be 1, otherwise 0

        # Check if the user is already registered in the dashboard
        cursor.execute("SELECT user_id FROM dashboard WHERE guild_id = %s AND user_id = %s", (guild.id, member.id))
        result = cursor.fetchone()

        if result is None:
            # Insert the new user into the dashboard with the corresponding values
            cursor.execute(
                "INSERT INTO dashboard (guild_id, user_id, user_username, user_nickname, date_joined, is_active, is_bot, is_admin, user_privilege) VALUES (%s, %s, %s, %s, NOW(), 1, %s, %s, 1)",
                (guild.id, member.id, member.name, member.display_name, is_bot, is_admin)
            )
            db.commit()
            print(f"Member {member.name} added to dashboard for guild {guild.name}.")
        else:
            # Update the user's values if they are already registered
            cursor.execute(
                "UPDATE dashboard SET user_username = %s, user_nickname = %s, is_bot = %s, is_admin = %s WHERE guild_id = %s AND user_id = %s",
                (member.name, member.display_name, is_bot, is_admin, guild.id, member.id)
            )
            db.commit()
            print(f"Member {member.name} updated in dashboard for guild {guild.name}.")

        # Now handle the user's roles
        register_user_roles(guild.id, member)


def register_user_roles(guild_id, member):
    # Delete all current roles for this user in this guild (if you want to maintain synchronization)
    cursor.execute("DELETE FROM user_roles WHERE guild_id = %s AND user_id = %s", (guild_id, member.id))
    db.commit()

    # Insert the user's current roles
    for role in member.roles:
        if role.is_default():
            continue  # We don't want to register the default role (such as @everyone)

        cursor.execute(
            "INSERT INTO user_roles (guild_id, user_id, role_id, role_name) VALUES (%s, %s, %s, %s)",
            (guild_id, member.id, role.id, role.name)
        )
        db.commit()
        print(f"Role {role.name} added for member {member.name} in guild {guild_id}.")



def update_user_status(guild):
    # Get list of users on server from database
    cursor.execute("SELECT user_id FROM dashboard WHERE guild_id = %s", (guild.id,))
    stored_users = cursor.fetchall()  # List of users in the database

    # Get current list of members from server
    guild_members = {member.id for member in guild.members}  # Set with the IDs of the current members

    # Check if stored users are still on the server
    for (user_id,) in stored_users:
        if user_id not in guild_members:
            # User kicked, update status to inactive
            cursor.execute("UPDATE dashboard SET is_active = 0 WHERE guild_id = %s AND user_id = %s", (guild.id, user_id))
            db.commit()
            print(f"User {user_id} marked as inactive in guild {guild.name}.")
        else:
            # User is still on the server, ensure it is active
            cursor.execute("UPDATE dashboard SET is_active = 1 WHERE guild_id = %s AND user_id = %s", (guild.id, user_id))
            db.commit()




@bot.event
async def on_ready():
    print(f'Bot started as {bot.user.name}')

    # Ensure all necessary tables exist
    ensure_tables_exist()

    # Start the scheduler in a separate thread
   # Uncomment this line when deployed in production 
   #  threading.Thread(target=schedule_restart).start()
    
    # Register servers where the bot is already present

    for guild in bot.guilds:
        register_server(guild)

    # update users

    for guild in bot.guilds:
        update_user_status(guild)


    # Change bot presence
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="www.abbybot.cl", 
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
    await bot.add_cog(EventsControl(bot))
    await bot.add_cog(Blackjack(bot))
    await bot.add_cog(WaifuImg(bot))
    await bot.add_cog(CatImg(bot))
    await bot.add_cog(NekoImg(bot))
    await bot.add_cog(DogImg(bot))
    await bot.add_cog(SetPrefix(bot))
    await bot.add_cog(ServerInfo(bot))
    await bot.add_cog(UserInfo(bot))
    await bot.add_cog(SetBirthday(bot))
    
    # Sync slash commands globally or to specific guilds
    try:
        synced_commands = await bot.tree.sync()
        print(f"Successfully synced {len(synced_commands)} commands.")
    except Exception as e:
        print(f"An error occurred while syncing commands: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore bot messages

    guild_id = message.guild.id  # get guild ID (Server ID)

    try:
        # Reopen DB
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Query custom prefix from database
        cursor.execute("SELECT prefix FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result:
            prefix = result[0]
        else:
            prefix = 'abbybot_'  # Use the default prefix if it is not found in the database

        # Check if the message starts with the prefix
        if message.content.startswith(prefix):
            
            # Process the command
            
            await message.channel.send(f"Prefix detected! The prefix for this server is: `{prefix}`")

            await bot.process_commands(message)

    except mysql.connector.Error as err:
        print(f"Error interacting with MySQL: {err}")

    finally:

        # close cursor or db

        if cursor:
            cursor.close()
        if db:
            db.close()

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

