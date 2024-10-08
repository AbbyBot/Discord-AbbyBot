import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import mysql.connector
import sys
import schedule
import time
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime

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
from chat_commands.ping import Ping
from chat_commands.code import Code
from chat_commands.help import Help
from chat_commands.tell_history import TellHistory
from chat_commands.server_commands import ServerCommands


from chat_commands.user_commands import UserCommands

# Settings commands import

from settings_commands.set_commands import SetCommands

# Events import
from event_commands.deleted_messages import Deleted_Messages
from event_commands.Abby_mentions import Abby_mentions
from event_commands.birthday_events import BirthdayEvent

# Control commands import
from settings_commands.control_commands import ControlGroup

# Event Roles

from event_commands.roles.on_guild_role_create import RoleCreateEvent
from event_commands.roles.on_guild_role_delete import RoleDeleteEvent
from event_commands.roles.on_guild_role_update import RoleUpdateEvent

# Event Guild channel

from event_commands.guild.on_guild_channel_create import ChannelCreateEvent
from event_commands.guild.on_guild_channel_delete import ChannelDeleteEvent
from event_commands.guild.on_guild_channel_update import ChannelUpdateEvent

# Minigames import
from minigames.minigames_commands import Minigames_commands


# APIs commands import
from api_commands.image_commands import ImageCommands
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

# Function to download and save the icon
def download_and_save_icon(guild_id, guild_icon_url):
    try:
        response = requests.get(guild_icon_url)
        img = Image.open(BytesIO(response.content))

        # Convert to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        image_filename = f"{guild_id}.jpg"
        image_path = os.path.join(IMAGE_FOLDER, image_filename)
        img.save(image_path, "JPEG")
        print(f"Image saved at: {image_path}")

        return image_filename
    except Exception as e:
        print(f"Error downloading or saving the server's icon: {e}")
        return '0.png'


# Path of the folder where the images will be stored
IMAGE_FOLDER = os.getenv('IMAGE_FOLDER_PATH')

# Function to register or update a server
def register_server(guild, cursor, db):
    # Assign default value of 1 for language if not obtained from database
    default_language_id = 1
    
    cursor.execute("SELECT guild_id, guild_icon_url FROM server_settings WHERE guild_id = %s", (guild.id,))
    result = cursor.fetchone()

    # Assign default value of 1 for language if not obtained from database
    guild_icon_url = str(guild.icon.url) if guild.icon else None  # Use the URL if it has an icon
    
    if result is None:
        # Register the server for the first time
        cursor.execute("""
            INSERT INTO server_settings 
            (guild_id, guild_name, owner_id, member_count, prefix, guild_language, guild_icon_url, guild_icon_last_updated) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            (guild.id, guild.name, guild.owner.id, guild.member_count, 'abbybot_', default_language_id, guild_icon_url, datetime.now())
        )
        print(f"Server {guild.name} registered.")
    else:
        # If are already registered, update only if the icon URL has changed
        stored_icon_url = result[1]  # The URL stored in the database
        if guild_icon_url != stored_icon_url:
            cursor.execute("""
                UPDATE server_settings 
                SET guild_name = %s, owner_id = %s, member_count = %s, guild_icon_url = %s, guild_icon_last_updated = %s
                WHERE guild_id = %s
                """, 
                (guild.name, guild.owner.id, guild.member_count, guild_icon_url, datetime.now(), guild.id)
            )
            print(f"Server {guild.name} updated.")
    
    db.commit()



    # Register or update the members of the server
    register_members(guild, cursor, db)

def register_members(guild, cursor, db):
    for member in guild.members:
        is_bot = 1 if member.bot else 0
        is_admin = 1 if member.guild_permissions.administrator else 0

        # Get user created_at date
        account_created_at = member.created_at

        # Obtain the user's nickname on the server, if they do not have a nickname, use the username
        user_server_nickname = member.nick if member.nick else member.name

        # Register or update user in user_profile (global data)
        cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (member.id,))
        user_profile = cursor.fetchone()

        if user_profile is None:
            # Insert new user into user_profile if not exists
            cursor.execute("""
                INSERT INTO user_profile 
                (user_id, user_username, account_created_at, user_privilege) 
                VALUES (%s, %s, %s, 1)
                """, 
                (member.id, member.name, account_created_at)
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
                (guild_id, user_profile_id, is_bot, is_admin, user_server_nickname) 
                VALUES (%s, %s, %s, %s, %s)
                """, 
                (guild.id, user_profile_id, is_bot, is_admin, user_server_nickname)
            )
        else:
            cursor.execute("""
                UPDATE dashboard 
                SET is_bot = %s, is_admin = %s, user_server_nickname = %s
                WHERE guild_id = %s AND user_profile_id = %s
                """, 
                (is_bot, is_admin, user_server_nickname, guild.id, user_profile_id)
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
        
        # Loop through all guilds that the bot is a member of
        for guild in bot.guilds:
            # Fetch the stored icon URL from the database
            cursor.execute("SELECT guild_icon_url FROM server_settings WHERE guild_id = %s", (guild.id,))
            result = cursor.fetchone()

            if result:
                stored_icon_path = result[0]
                guild_icon_url = str(guild.icon.url) if guild.icon else None

                if guild_icon_url:
                    # Compare the stored icon with the current icon
                    if not stored_icon_path or not os.path.exists(stored_icon_path) or has_icon_changed(guild_icon_url, stored_icon_path):
                        # Update the server icon if changed or the file does not exist
                        update_server_icon(guild, cursor, db)

            # Register the server and update user statuses
            register_server(guild, cursor, db)
            update_user_status(guild, cursor, db)

    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="abbybotproject.com"
    ))

    # Load all commands (cogs)
    await bot.add_cog(Ping(bot))
    await bot.add_cog(Code(bot))
    await bot.add_cog(Deleted_Messages(bot))
    await bot.add_cog(Abby_mentions(bot))
    await bot.add_cog(Help(bot))

    await bot.add_cog(TellHistory(bot))

    await bot.add_cog(SetCommands(bot))
    await bot.add_cog(ControlGroup(bot))

    
    await bot.add_cog(Minigames_commands(bot))
    await bot.add_cog(ImageCommands(bot))
    await bot.add_cog(ServerCommands(bot))
    await bot.add_cog(UserCommands(bot))


    await bot.add_cog(BirthdayEvent(bot))


    # Events
    await bot.add_cog(RoleCreateEvent(bot))
    await bot.add_cog(RoleDeleteEvent(bot))
    await bot.add_cog(RoleUpdateEvent(bot))

    # Channels

    await bot.add_cog(ChannelCreateEvent(bot))
    await bot.add_cog(ChannelDeleteEvent(bot))
    await bot.add_cog(ChannelUpdateEvent(bot))
    


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
async def on_guild_update(before, after):
    # Check if the icon has changed
    if before.icon != after.icon:
        print(f"Icon changed for {after.name}")
        
        with get_db_connection() as db:
            cursor = db.cursor()
            
            # Call a function to update the server icon
            update_server_icon(after, cursor, db)

# Function to check if the icon has changed by comparing current URL with the stored file
def has_icon_changed(guild_icon_hash, stored_icon_hash):
    return guild_icon_hash != stored_icon_hash



# Function to update the server icon if it has changed
def update_server_icon(guild, cursor, db):
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    guild_icon_url = str(guild.icon.url) if guild.icon else None

    if guild_icon_url:
        cursor.execute("SELECT guild_icon_url FROM server_settings WHERE guild_id = %s", (guild.id,))
        result = cursor.fetchone()
        stored_icon_filename = result[0] if result else None

        if stored_icon_filename and not has_icon_changed(guild_icon_url, stored_icon_filename):
            print(f"Icon has not changed for {guild.name}, skipping update.")
            return

        image_filename = download_and_save_icon(guild.id, guild_icon_url)

        cursor.execute("""
            UPDATE server_settings 
            SET guild_icon_url = %s, guild_icon_last_updated = %s
            WHERE guild_id = %s
            """, 
            (image_filename, datetime.now(), guild.id)
        )
        db.commit()


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
            
            # Fetch the current icon URL before deleting the server entry
            cursor.execute("SELECT guild_icon_url FROM server_settings WHERE guild_id = %s", (guild.id,))
            result = cursor.fetchone()
            if result:
                icon_path = result[0]
                if os.path.exists(icon_path):
                    os.remove(icon_path)  # Delete the server icon file
                    print(f"Deleted server icon file at: {icon_path}")
            
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
async def on_member_update(before, after):
    guild_id = after.guild.id
    user_id = after.id

    # Get the roles before and after the change
    before_roles = set(before.roles)
    after_roles = set(after.roles)

    # Compare previous roles with new ones
    added_roles = after_roles - before_roles
    removed_roles = before_roles - after_roles

    with get_db_connection() as db:
        cursor = db.cursor()

        # If there are added roles
        for role in added_roles:
            if not role.is_default():  # Ignore the default "Everyone" role
                cursor.execute("""
                    INSERT INTO user_roles (guild_id, user_profile_id, role_id, role_name) 
                    VALUES (%s, (SELECT id FROM user_profile WHERE user_id = %s), %s, %s)
                    """, 
                    (guild_id, user_id, role.id, role.name)
                )
                db.commit()

        # If there are deleted roles
        for role in removed_roles:
            if not role.is_default():  # Ignore the default "Everyone" role
                cursor.execute("""
                    DELETE FROM user_roles 
                    WHERE guild_id = %s AND user_profile_id = (SELECT id FROM user_profile WHERE user_id = %s) AND role_id = %s
                    """, 
                    (guild_id, user_id, role.id)
                )
                db.commit()



@bot.event
async def on_close():
    print("Bot is shutting down.")

try:
    bot.run(token)
except Exception as e:
    print(f"An error occurred: {e}")