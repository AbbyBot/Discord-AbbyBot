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


# Path of the folder where the images will be stored
IMAGE_FOLDER = os.getenv('IMAGE_FOLDER_PATH')

# Register new server or update an existing server
def register_server(guild, cursor, db):
    # Ensure the image folder exists, if not, create it
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    # Fetch default language ID (assuming 'en' is default)
    cursor.execute("SELECT id FROM languages WHERE language_code = %s", ('en',))
    default_language_id = cursor.fetchone()[0]

    # Check if the server already exists in the database
    cursor.execute("SELECT guild_id FROM server_settings WHERE guild_id = %s", (guild.id,))
    if cursor.fetchone() is None:
        # If the server is new, retrieve the icon URL
        guild_icon_url = str(guild.icon.url) if guild.icon else None
        image_path = None

        if guild_icon_url:
            try:
                # Download the image from the server's icon URL
                response = requests.get(guild_icon_url)
                img = Image.open(BytesIO(response.content))

                # Convert the image to JPG format
                img = img.convert("RGB")

                # Generate a unique filename using guild_id and current date
                date_str = datetime.now().strftime('%Y%m%d%H%M%S')
                image_filename = f"{guild.id}_{date_str}.jpg"
                image_path = os.path.join(IMAGE_FOLDER, image_filename)

                # Save the image as a JPG file
                img.save(image_path, "JPEG")
                print(f"Image saved at: {image_path}")

                # Solo almacena el nombre del archivo en la base de datos
                image_url = image_filename

            except Exception as e:
                print(f"Error downloading or saving the server's icon: {e}")
        
        # Insert the new server's data into the database
        cursor.execute("""
            INSERT INTO server_settings 
            (guild_id, guild_name, owner_id, member_count, prefix, guild_language, guild_icon_url, guild_icon_last_updated) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            (guild.id, guild.name, guild.owner.id, guild.member_count, 'abbybot_', default_language_id, image_url, datetime.now())
        )
        print(f"Server {guild.name} registered.")
    else:
        # If the server already exists, update its details
        cursor.execute("""
            UPDATE server_settings 
            SET guild_name = %s, owner_id = %s, member_count = %s 
            WHERE guild_id = %s
            """, 
            (guild.name, guild.owner.id, guild.member_count, guild.id)
        )
        print(f"Server {guild.name} updated.")
    
    # Commit the changes to the database
    db.commit()

    # Register or update the members of the server
    register_members(guild, cursor, db)

def register_members(guild, cursor, db):
    for member in guild.members:
        is_bot = 1 if member.bot else 0
        is_admin = 1 if member.guild_permissions.administrator else 0

        # Full date and time format as timestamp (YYYY-MM-DD HH:MM:SS)
        account_created_at = member.created_at.strftime('%Y-%m-%d %H:%M:%S')

        # Register or update user in user_profile (global data)
        cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (member.id,))
        user_profile = cursor.fetchone()

        if user_profile is None:
            # Insert new user into user_profile if not exists
            cursor.execute("""
                INSERT INTO user_profile 
                (user_id, user_username, user_privilege, account_created_at) 
                VALUES (%s, %s, 1, %s)
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
async def on_guild_update(before, after):
    # Check if the icon has changed
    if before.icon != after.icon:
        print(f"Icon changed for {after.name}")
        
        with get_db_connection() as db:
            cursor = db.cursor()
            
            # Call a function to update the server icon
            update_server_icon(after, cursor, db)

# Function to check if the icon has changed by comparing current URL with the stored file
def has_icon_changed(current_icon_url, stored_icon_filename):
    try:
        # Download the current icon image
        response = requests.get(current_icon_url)
        current_icon = Image.open(BytesIO(response.content))

        # Genera la ruta completa del archivo almacenado
        stored_icon_path = os.path.join(IMAGE_FOLDER, stored_icon_filename)

        # Open the stored icon image
        stored_icon = Image.open(stored_icon_path)

        # Compare sizes as a simple check (you can expand this to pixel-by-pixel comparison)
        if current_icon.size != stored_icon.size:
            return True
        
        return False

    except Exception as e:
        print(f"Error comparing icons: {e}")
        return True  # Assume icon has changed if there's an error



# Function to update the server icon if it has changed
def update_server_icon(guild, cursor, db):
    # Ensure the image folder exists
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    # Get the new icon URL
    guild_icon_url = str(guild.icon.url) if guild.icon else None
    image_path = None

    if guild_icon_url:
        try:
            # Download the new icon image
            response = requests.get(guild_icon_url)
            img = Image.open(BytesIO(response.content))

            # Convert the image to JPG format
            img = img.convert("RGB")

            # Generate a unique filename using guild_id and current date
            date_str = datetime.now().strftime('%Y%m%d%H%M%S')
            image_filename = f"{guild.id}_{date_str}.jpg"
            image_path = os.path.join(IMAGE_FOLDER, image_filename)

            # Save the image
            img.save(image_path, "JPEG")
            print(f"New icon saved at: {image_path}")

            # Only store the file name in the database
            image_url = image_filename
            cursor.execute("""
                UPDATE server_settings 
                SET guild_icon_url = %s, guild_icon_last_updated = %s
                WHERE guild_id = %s
                """, 
                (image_url, datetime.now(), guild.id)
            )
            db.commit()

        except Exception as e:
            print(f"Error downloading or saving the new icon: {e}")

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
async def on_close():
    print("Bot is shutting down.")

try:
    bot.run(token)
except Exception as e:
    print(f"An error occurred: {e}")
