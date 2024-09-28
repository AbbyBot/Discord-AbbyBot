import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import mysql.connector
import sys
import schedule
import time

# Load dotenv variables
load_dotenv()

# Bot_token from .env
token = os.getenv("BOT_TOKEN")

# MySQL connection setup
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# Chat commands import
from chat_commands.Ping import Ping
from chat_commands.Code import Code
from chat_commands.Help import Help
from chat_commands.TellHistory import TellHistory
from chat_commands.server_info import ServerInfo
from chat_commands.User_info import UserInfo

# Settings commands import
from settings_commands.Set_language import SetLanguage
from settings_commands.Events_control import EventsControl
from settings_commands.set_prefix import SetPrefix
from settings_commands.Set_birthday import SetBirthday
from settings_commands.Set_birthday_channel import SetBirthDayChannel
from settings_commands.Set_logs_channel import SetLogsChannel

# Events import
from event_codes.Deleted_messages import Deleted_Messages
from event_codes.Abby_mentions import Abby_mentions

# Minigames import
from minigames.blackjack import Blackjack
from minigames.RockPaperScissors import RockPaperScissors

# APIs commands import
from api_commands.waifu_img import WaifuImg
from api_commands.cat_img import CatImg
from api_commands.neko_img import NekoImg
from api_commands.dog_img import DogImg

# Establish MySQL connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to restart the bot
def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)
    print("Bot is restarting...")

# Scheduler to restart the bot every hour
def schedule_restart():
    schedule.every(2).hours.do(restart_bot)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Ensure necessary tables exist in the database
def ensure_tables_exist(cursor):
    tables = ['server_settings', 'dashboard', 'user_profile', 'mention_counter']
    for table in tables:
        cursor.execute(f"SHOW TABLES LIKE '{table}';")
        if cursor.fetchone() is None:
            print(f"Table {table} does not exist. You should create it.")
        else:
            print(f"Table {table} already exists.")

# Register new server or update an existing server
def register_server(guild, cursor, db):
    cursor.execute("SELECT id FROM languages WHERE language_code = %s", ('en',))
    default_language_id = cursor.fetchone()[0]

    cursor.execute("SELECT guild_id FROM server_settings WHERE guild_id = %s", (guild.id,))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO server_settings 
            (guild_id, guild_name, owner_id, member_count, prefix, guild_language) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """, 
            (guild.id, guild.name, guild.owner.id, guild.member_count, 'abbybot_', default_language_id)
        )
        print(f"Server {guild.name} registered.")
    else:
        cursor.execute("""
            UPDATE server_settings 
            SET guild_name = %s, owner_id = %s, member_count = %s 
            WHERE guild_id = %s
            """, 
            (guild.name, guild.owner.id, guild.member_count, guild.id)
        )
        print(f"Server {guild.name} updated.")
    
    db.commit()
    register_members(guild, cursor, db)

# Register or update members in the guild
def register_members(guild, cursor, db):
    for member in guild.members:
        is_bot = 1 if member.bot else 0
        is_admin = 1 if member.guild_permissions.administrator else 0

        # Register or update user in user_profile (global data)
        cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (member.id,))
        user_profile = cursor.fetchone()

        if user_profile is None:
            # Insert new user into user_profile if not exists
            cursor.execute("""
                INSERT INTO user_profile 
                (user_id, user_username, user_privilege) 
                VALUES (%s, %s, 1)
                """, 
                (member.id, member.name)
            )
            db.commit()

            # Retrieve the new user_profile_id
            cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (member.id,))
            user_profile = cursor.fetchone()

        user_profile_id = user_profile[0]

        # Register or update member data in dashboard (server-specific data)
        cursor.execute("SELECT id FROM dashboard WHERE guild_id = %s AND user_profile_id = %s", (guild.id, user_profile_id))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO dashboard 
                (guild_id, user_profile_id, is_bot, is_admin) 
                VALUES (%s, %s, %s, %s)
                """, 
                (guild.id, user_profile_id, is_bot, is_admin)
            )
        else:
            cursor.execute("""
                UPDATE dashboard 
                SET is_bot = %s, is_admin = %s 
                WHERE guild_id = %s AND user_profile_id = %s
                """, 
                (is_bot, is_admin, guild.id, user_profile_id)
            )

        db.commit()
        register_user_roles(guild.id, member, cursor, db)


# Register or update user roles
def register_user_roles(guild_id, member, cursor, db):
    cursor.execute("DELETE FROM user_roles WHERE guild_id = %s AND user_profile_id = (SELECT id FROM user_profile WHERE user_id = %s)", (guild_id, member.id))
    db.commit()

    for role in member.roles:
        if not role.is_default():
            cursor.execute("""
                INSERT INTO user_roles (guild_id, user_profile_id, role_id, role_name) 
                VALUES (%s, (SELECT id FROM user_profile WHERE user_id = %s), %s, %s)
                """, 
                (guild_id, member.id, role.id, role.name)
            )
            db.commit()

# Update user status (active/inactive) without overriding previous inactive status
def update_user_status(guild, cursor, db):
    # Get all registered users in the database for this server, now from `user_profile` via a join with `dashboard`
    cursor.execute("""
        SELECT up.user_id, up.is_active 
        FROM user_profile up
        JOIN dashboard d ON up.id = d.user_profile_id 
        WHERE d.guild_id = %s
    """, (guild.id,))
    stored_users = cursor.fetchall()

    # Create a set of current server members' user IDs
    guild_members = {member.id for member in guild.members}

    # Update the status of each user
    for user_id, is_active in stored_users:
        # If the user is already inactive (is_active = 0), do not change its status
        if is_active == 0:
            continue

        # If the user is on the server, mark them as active, otherwise inactive
        new_status = 1 if user_id in guild_members else 0
        cursor.execute("""
            UPDATE user_profile 
            SET is_active = %s 
            WHERE user_id = %s
        """, (new_status, user_id))

    db.commit()



# Discord bot setup
bot = commands.Bot(command_prefix='abbybot_', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot started as {bot.user.name}')
    
    with get_db_connection() as db:
        cursor = db.cursor()
        ensure_tables_exist(cursor)
        
        for guild in bot.guilds:
            register_server(guild, cursor, db)
            update_user_status(guild, cursor, db)

    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="www.abbybot.cl"
    ))

    # Load all commands (cogs)
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
    await bot.add_cog(SetBirthDayChannel(bot))
    await bot.add_cog(SetLogsChannel(bot))

    try:
        synced_commands = await bot.tree.sync()
        print(f"Successfully synced {len(synced_commands)} commands.")
    except Exception as e:
        print(f"An error occurred while syncing commands: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # If message is DM
    if isinstance(message.channel, discord.DMChannel):
        embed = discord.Embed(
            title="Greetings!",
            description="AbbyBot does not have a DM system, if you need to know information about the Bot, you can run */help* or go to this [Commands URL](https://abbybot.cl/commands-list).",
            color=0xb45428
        )
        embed.set_footer(text="AbbyBot Project - Always here to help.")
        await message.channel.send(embed=embed)
    else:
        # handle regular messages on servers
        guild_id = message.guild.id
        with get_db_connection() as db:
            cursor = db.cursor()

            cursor.execute("SELECT prefix FROM server_settings WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            prefix = result[0] if result else 'abbybot_'

            if message.content.startswith(prefix):
                await message.channel.send(f"Prefix detected! The prefix for this server is: `{prefix}`")
                await bot.process_commands(message)



@bot.event
async def on_guild_remove(guild):
    # Delete server data when AbbyBot is kicked
    with get_db_connection() as db:
        cursor = db.cursor()
        
        try:
            # Delete records in the `mention_counter` table related to the server
            cursor.execute("DELETE FROM mention_counter WHERE user_server = %s", (guild.id,))
            
            # Delete server-related `user_roles` records
            cursor.execute("DELETE FROM user_roles WHERE guild_id = %s", (guild.id,))
            
            # Delete server-related `dashboard` logs
            cursor.execute("DELETE FROM dashboard WHERE guild_id = %s", (guild.id,))
            
            # Finally, remove the server from the `server_settings` table
            cursor.execute("DELETE FROM server_settings WHERE guild_id = %s", (guild.id,))
            
            # Commit changes
            db.commit()
            print(f"All data related to server '{guild.name}' (ID: {guild.id}) has been deleted.")
        except Exception as e:
            db.rollback()  # Rollback if something fails
            print(f"Error deleting data for server '{guild.name}' (ID: {guild.id}): {e}")

@bot.event
async def on_guild_join(guild):
    # Reuse existing event to register servers
    with get_db_connection() as db:
        cursor = db.cursor()
        register_server(guild, cursor, db)
    print(f"Joined and registered new server: {guild.name}")


@bot.event
async def on_close():
    print("Bot is shutting down.")

try:
    bot.run(token)
except Exception as e:
    print(f"An error occurred: {e}")
