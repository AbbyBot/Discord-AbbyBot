import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import random
import signal
from xp_system.xp_events import add_xp
import asyncio


# utils/AbbyBot-Main functions
from utils.AbbyBot_Main.get_db_connection import get_db_connection
from utils.AbbyBot_Main.server_data.ensure_tables_exists import ensure_tables_exist
from utils.AbbyBot_Main.server_data.register_server import register_server
from utils.AbbyBot_Main.users.update_user_status import update_user_status
from utils.AbbyBot_Main.server_data.clean_disconnected_servers import clean_disconnected_servers
from utils.AbbyBot_Main.server_data.register_channels import register_channels
from utils.AbbyBot_Main.API.notify_api_status import notify_api_status
from utils.AbbyBot_Main.server_data.update_server_icon import update_server_icon
from utils.AbbyBot_Main.API.handle_shutdown import handle_shutdown
from utils.AbbyBot_Main.API.notify_api_status import  update_bot_info

# Load dotenv variables
load_dotenv()

# Bot_token from .env
token = os.getenv("BOT_TOKEN")

# Chat commands import
from chat_commands.ping import Ping
from chat_commands.help import Help
from chat_commands.tell_history import TellGroup
from chat_commands.server_commands import ServerCommands
from chat_commands.user_commands import UserCommands

# Settings commands import

from settings_commands.set_commands import SetCommands

# Events import
from event_commands.deleted_messages import Deleted_Messages
from event_commands.abbybot_mentions import abbybot_mentions
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

# Members role
from event_commands.members.on_member_update import MemberUpdateEvent


# APIs commands import
from api_commands.image_commands import ImageCommands
from api_commands.fortnite_commands import FortniteCommands


# Premium commands

from premium_commands.music_player import MusicPlayer

print(r'''
    ___    __    __          ____        __     ____               _           __ 
   /   |  / /_  / /_  __  __/ __ )____  / /_   / __ \_________    (_)__  _____/ /_
  / /| | / __ \/ __ \/ / / / __  / __ \/ __/  / /_/ / ___/ __ \  / / _ \/ ___/ __/
 / ___ |/ /_/ / /_/ / /_/ / /_/ / /_/ / /_   / ____/ /  / /_/ / / /  __/ /__/ /_  
/_/  |_/_.___/_.___/\__, /_____/\____/\__/  /_/   /_/   \____/_/ /\___/\___/\__/  
                   /____/                                   /___/                   
                             "Your best friend on your Discord server"    
      ''')


# Discord bot setup
bot = commands.Bot(command_prefix='abbybot_', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("\033[34m" + 'Bot started as ' + bot.user.name + "\033[0m")

    # Notify the API that AbbyBot is online
    notify_api_status("online")

    # Update bot info to AbbyBot API
    update_bot_info(bot)
    
    with get_db_connection() as db:
        cursor = db.cursor()
        ensure_tables_exist(cursor)

        # Get IDs of the servers where the bot is currently
        active_guild_ids = {guild.id for guild in bot.guilds}
        
        # Delete servers data that are no longer active
        clean_disconnected_servers(cursor, db, active_guild_ids)
        
        # Loop through all guilds that the bot is a member of
        for guild in bot.guilds:

            # Register the server and update user statuses
            register_server(guild, cursor, db)
            update_user_status(guild, cursor, db)
            
            # Check and update name and icon when starting the bot
            cursor.execute("SELECT guild_name, guild_icon_url FROM server_settings WHERE guild_id = %s", (guild.id,))
            result = cursor.fetchone()
            
            if result:
                stored_name, stored_icon_url = result
                
                # Compare and update server name
                if guild.name != stored_name:
                    cursor.execute("""
                        UPDATE server_settings 
                        SET guild_name = %s 
                        WHERE guild_id = %s
                    """, (guild.name, guild.id))
                    print(f"\033[34mUpdated server name for guild ID {guild.id} to '{guild.name}'\033[0m")

                # Get Icon URL or default URL
                random_avatar = random.randint(1, 5)
                current_icon_url = str(guild.icon.url) if guild.icon else f'https://cdn.discordapp.com/embed/avatars/{random_avatar}.png'

                # Compare and change photo
                if current_icon_url != stored_icon_url:
                    cursor.execute("""
                        UPDATE server_settings 
                        SET guild_icon_url = %s, guild_icon_last_updated = %s 
                        WHERE guild_id = %s
                    """, (current_icon_url, datetime.now(), guild.id))
                    print(f"\033[34mUpdated server icon for guild ID {guild.id}\033[0m")

            # Register or update server channels
            register_channels(guild, cursor, db)

            db.commit()

    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="abbybotproject.com"
    ))

    # Load all commands (cogs)
    await bot.add_cog(Ping(bot))
    await bot.add_cog(Deleted_Messages(bot))
    await bot.add_cog(abbybot_mentions(bot))
    await bot.add_cog(Help(bot))

    await bot.add_cog(TellGroup(bot))

    await bot.add_cog(SetCommands(bot))
    await bot.add_cog(ControlGroup(bot))

    
    await bot.add_cog(Minigames_commands(bot))
    await bot.add_cog(ImageCommands(bot))
    await bot.add_cog(FortniteCommands(bot))
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


    await bot.add_cog(MemberUpdateEvent(bot))
    
    await bot.add_cog(MusicPlayer(bot))

    try:
        synced_commands = await bot.tree.sync()
        print(f"Successfully synced {len(synced_commands)} commands.")
    except Exception as e:
        print(f"An error occurred while syncing commands: {e}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        embed = discord.Embed(
            title="Greetings!",
            description="AbbyBot does not have a DM system, if you need to know information about the Bot, you can run */help* or go to this [Commands URL](https://abbybotproject.com/commands).",
            color=0xb45428
        )
        embed.set_footer(text="AbbyBot Project - Always here to help.")
        await message.channel.send(embed=embed)
    else:
        guild_id = message.guild.id
        with get_db_connection() as db:
            cursor = db.cursor()

            cursor.execute("SELECT prefix FROM server_settings WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            prefix = result[0] if result else 'abbybot_'

            if message.content.startswith(prefix):
                await message.channel.send(f"Prefix detected! The prefix for this server is: `{prefix}`")
                await bot.process_commands(message)

            # Add XP for sending messages, applying the XP privilege multiplier
            user_id = message.author.id
            add_xp(user_id, 10, "message_sent", cursor, db)

        await bot.process_commands(message)

@bot.event
async def on_guild_update(before, after):
    with get_db_connection() as db:
        cursor = db.cursor()
        
        # Check is server name changed
        if before.name != after.name:
            cursor.execute("""
                UPDATE server_settings 
                SET guild_name = %s 
                WHERE guild_id = %s
            """, (after.name, after.id))
            db.commit()
            print(f"\033[34mServer name updated to '{after.name}' for guild ID {after.id}\033[0m")
        
        # Check icon change
        if before.icon != after.icon:
            update_server_icon(after, cursor, db)

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
            
            # Remove the server from the `server_settings` table
            cursor.execute("DELETE FROM server_settings WHERE guild_id = %s", (guild.id,))
            
            # Commit changes
            db.commit()

            print("\033[32m" + f"All data related to server '{guild.name}' (ID: {guild.id}) has been deleted." + "\033[0m")
        except Exception as e:
            db.rollback()  # Rollback if something fails

            print("\033[31m" + f"Error deleting data for server '{guild.name}' (ID: {guild.id}): {e}" + "\033[0m")

@bot.event
async def on_guild_join(guild):
    # Reuse existing event to register servers
    with get_db_connection() as db:
        cursor = db.cursor()
        register_server(guild, cursor, db)
        print("\033[32m" + "Joined and registered new server: " + guild.name + "\033[0m")

@bot.event
async def on_member_update(before, after):
    guild_id = after.guild.id
    user_id = after.id

    # Get the roles before and after the change
    before_roles = set(before.roles)
    after_roles = set(after.roles)

    # Compare old roles with new ones
    added_roles = after_roles - before_roles
    removed_roles = before_roles - after_roles

    with get_db_connection() as db:
        cursor = db.cursor()

        # If there are added roles
        for role in added_roles:
            if not role.is_default():  # Ignore the default role "Everyone"
                cursor.execute("""
                    INSERT INTO user_roles (guild_id, user_profile_id, role_id, role_name) 
                    VALUES (%s, (SELECT id FROM user_profile WHERE user_id = %s), %s, %s)
                    """, 
                    (guild_id, user_id, role.id, role.name)
                )
                db.commit()

        # If there are deleted roles
        for role in removed_roles:
            if not role.is_default():  # Ignore the default role "Everyone"
                cursor.execute("""
                    DELETE FROM user_roles 
                    WHERE guild_id = %s AND user_profile_id = (SELECT id FROM user_profile WHERE user_id = %s) AND role_id = %s
                    """, 
                    (guild_id, user_id, role.id)
                )
                db.commit()

        # Check if nickname changed
        if before.display_name != after.display_name:
            before_nick = before.display_name if before.display_name else before.name
            after_nick = after.display_name if after.display_name else after.name

            
            cursor.execute("""
                UPDATE dashboard 
                SET user_server_nickname = %s 
                WHERE user_profile_id = (SELECT id FROM user_profile WHERE user_id = %s AND guild_id = %s)
                """, (after_nick, user_id, guild_id))
            db.commit()

            
            print("\033[34m" + "Nickname from " + "\033[31m" + before_nick + "\033[34m" + " changed to " + "\033[32m" + after_nick + "\033[34m" + " on server " + after.guild.name + "." + "\033[0m")

    # Print logic for added and removed roles
    if added_roles:
        print("\033[34m" + "Roles added to " + "\033[32m" + after.name + "\033[34m" + ": " + "\033[32m" + str([role.name for role in added_roles]) + "\033[0m")
    if removed_roles:
        print("\033[34m" + "Roles removed from " + "\033[32m" + after.name + "\033[34m" + ": " + "\033[31m" + str([role.name for role in removed_roles]) + "\033[0m")


def shutdown_handler(sig, frame): # This function is called when the bot is shutting down, Python and Docker
    handle_shutdown(sig, frame)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

async def main():
    async with bot:
        await bot.start(token)

asyncio.run(main())
