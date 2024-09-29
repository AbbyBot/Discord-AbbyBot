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
import hashlib

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

# Path where the images will be stored
IMAGE_FOLDER = os.getenv('IMAGE_FOLDER_PATH')

# Establish MySQL connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to restart the bot
def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)
    print("Bot is restarting...")

# Scheduler to restart the bot every two hours
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

# Function to register or update a server
def register_server(guild, cursor, db):
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    image_url = '0.png'  # Default value if no icon is found

    cursor.execute("SELECT id FROM languages WHERE language_code = %s", ('en',))
    default_language_id = cursor.fetchone()[0]

    cursor.execute("SELECT guild_id, guild_icon_url FROM server_settings WHERE guild_id = %s", (guild.id,))
    result = cursor.fetchone()

    guild_icon_url = str(guild.icon.url) if guild.icon else None

    if result is None:
        if guild_icon_url:
            image_url = download_and_save_icon(guild.id, guild_icon_url)

        cursor.execute("""
            INSERT INTO server_settings 
            (guild_id, guild_name, owner_id, member_count, prefix, guild_language, guild_icon_url, guild_icon_last_updated) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            (guild.id, guild.name, guild.owner.id, guild.member_count, 'abbybot_', default_language_id, image_url, datetime.now())
        )
        print(f"Server {guild.name} registered.")
    else:
        stored_image_url = result[1]
        if guild_icon_url and stored_image_url != guild_icon_url:
            image_url = download_and_save_icon(guild.id, guild_icon_url)

        cursor.execute("""
            UPDATE server_settings 
            SET guild_name = %s, owner_id = %s, member_count = %s, guild_icon_url = %s, guild_icon_last_updated = %s
            WHERE guild_id = %s
            """, 
            (guild.name, guild.owner.id, guild.member_count, image_url, datetime.now(), guild.id)
        )
        print(f"Server {guild.name} updated.")
    
    db.commit()

# Helper function to calculate the hash of an image
def calculate_image_hash(image):
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')  # Use PNG for consistency during hashing
    return hashlib.md5(image_bytes.getvalue()).hexdigest()

# Function to check if the icon has changed by comparing hashes
def has_icon_changed(current_icon_url, stored_icon_filename):
    try:
        response = requests.get(current_icon_url)
        current_icon = Image.open(BytesIO(response.content))

        stored_icon_path = os.path.join(IMAGE_FOLDER, stored_icon_filename)

        if not os.path.exists(stored_icon_path):
            return True

        stored_icon = Image.open(stored_icon_path)

        current_icon_hash = calculate_image_hash(current_icon)
        stored_icon_hash = calculate_image_hash(stored_icon)

        return current_icon_hash != stored_icon_hash

    except Exception as e:
        print(f"Error comparing icons: {e}")
        return True

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

# Discord bot setup
bot = commands.Bot(command_prefix='abbybot_', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot started as {bot.user.name}')
    
    with get_db_connection() as db:
        cursor = db.cursor()
        ensure_tables_exist(cursor)
        
        for guild in bot.guilds:
            cursor.execute("SELECT guild_icon_url FROM server_settings WHERE guild_id = %s", (guild.id,))
            result = cursor.fetchone()

            if result:
                stored_icon_path = result[0]
                guild_icon_url = str(guild.icon.url) if guild.icon else None

                if guild_icon_url:
                    if not stored_icon_path or not os.path.exists(stored_icon_path) or has_icon_changed(guild_icon_url, stored_icon_path):
                        update_server_icon(guild, cursor, db)

            register_server(guild, cursor, db)

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="www.abbybot.cl"))

@bot.event
async def on_guild_update(before, after):
    if before.icon != after.icon:
        print(f"Icon changed for {after.name}")
        with get_db_connection() as db:
            cursor = db.cursor()
            update_server_icon(after, cursor, db)

@bot.event
async def on_guild_remove(guild):
    with get_db_connection() as db:
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM mention_counter WHERE user_server = %s", (guild.id,))
            cursor.execute("DELETE FROM user_roles WHERE guild_id = %s", (guild.id,))
            cursor.execute("DELETE FROM dashboard WHERE guild_id = %s", (guild.id,))

            cursor.execute("SELECT guild_icon_url FROM server_settings WHERE guild_id = %s", (guild.id,))
            result = cursor.fetchone()
            if result:
                icon_path = result[0]
                if os.path.exists(icon_path):
                    os.remove(icon_path)
                    print(f"Deleted server icon file at: {icon_path}")

            cursor.execute("DELETE FROM server_settings WHERE guild_id = %s", (guild.id,))
            db.commit()
            print(f"All data related to server '{guild.name}' (ID: {guild.id}) has been deleted.")
        except Exception as e:
            db.rollback()
            print(f"Error deleting data for server '{guild.name}' (ID: {guild.id}): {e}")

@bot.event
async def on_guild_join(guild):
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
