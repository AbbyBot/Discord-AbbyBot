import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
from utils.utils import get_bot_avatar
from datetime import datetime

# Load dotenv variables
load_dotenv()

class ChannelUpdateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event: on_guild_channel_update
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        # Load dotenv variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        guild_id = before.guild.id

        # Check if the server has activated_logs = 1
        cursor.execute("SELECT activated_logs FROM server_settings WHERE guild_id = %s", (guild_id,))
        logs_result = cursor.fetchone()

        if logs_result is None or logs_result[0] == 0:
            # If it is not activated or there is no result, do nothing
            cursor.close()
            db.close()
            return

        # Check server language
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()
        

        if result is None:
            # If the server is not registered, do nothing
            cursor.close()
            db.close()
            return
        language_id = result[0]


        changes = []

        # Compare relevant attributes between 'before' and 'after'
        if before.name != after.name:
            changes.append(f"Channel name changed from **{before.name}** to **{after.name}**." if language_id == 1 else f"Nombre del canal cambiado de **{before.name}** a **{after.name}**.")

        if before.category != after.category:
            before_category = before.category.name if before.category else "No category"
            after_category = after.category.name if after.category else "No category"
            changes.append(f"Category changed from **{before_category}** to **{after_category}**." if language_id == 1 else f"Categoría cambiada de **{before_category}** a **{after_category}**.")

        # Only check for slowmode_delay if it's a TextChannel
        if isinstance(before, discord.TextChannel) and isinstance(after, discord.TextChannel):
            if before.slowmode_delay != after.slowmode_delay:
                changes.append(f"Slowmode delay changed from **{before.slowmode_delay}**s to **{after.slowmode_delay}**s." if language_id == 1 else f"El retraso del modo lento cambió de **{before.slowmode_delay}**s a **{after.slowmode_delay}**s.")

        # Only check for topic if it's a TextChannel
        if isinstance(before, discord.TextChannel) and isinstance(after, discord.TextChannel):
            if (before.topic or "No topic") != (after.topic or "No topic"):  # Ensure empty topics are treated as 'No topic'
                before_topic = before.topic if before.topic else "No topic"
                after_topic = after.topic if after.topic else "No topic"
                changes.append(f"Channel topic changed from **{before_topic}** to **{after_topic}**." if language_id == 1 else f"El tema del canal cambió de **{before_topic}** a **{after_topic}**.")


        # If there are changes, format them as a bulleted list
        if changes:
            formatted_changes = "\n".join([f"{change}" for change in changes])

        # If there are no changes, exit the function
        if not changes:
            cursor.close()
            db.close()
            return

        # Check language and create response message
        
        # Get server icon from db
        cursor.execute("SELECT guild_icon_url FROM server_settings WHERE guild_id = %s", (guild_id,))
        guild_avatar_url = cursor.fetchone()

        # Get AbbyBot ID and icon
        bot_id = 1028065784016142398  # AbbyBot ID
        abbyBot_guild_icon = await get_bot_avatar(self.bot, bot_id)


        if guild_avatar_url is None or not guild_avatar_url[0].startswith("http"):
            
            guild_avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  
        else:
            guild_avatar_url = guild_avatar_url[0]



        if language_id == 1:
            now = datetime.now()
            english_datetime = now.strftime("%m/%d/%Y %H:%M:%S")
            embed = discord.Embed(
                title="Updates to channel",
                description=f"The channel {before.name} has been updated.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=guild_avatar_url)
            embed.add_field(name="Date and time", value=english_datetime, inline=True)
            embed.add_field(name="Changes", value=formatted_changes, inline=False)  # Use formatted changes
            embed.set_footer(
                text="AbbyBot",  
                icon_url=abbyBot_guild_icon  
            )

        elif language_id == 2:
            now = datetime.now()
            spanish_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
            embed = discord.Embed(
                title="Actualizaciones del canal",
                description=f"El canal {before.name} ha sido actualizado.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=guild_avatar_url)
            embed.add_field(name="Fecha y hora", value=spanish_datetime, inline=True)
            embed.add_field(name="Lista de cambios", value=formatted_changes, inline=False)  # Use formatted changes
            embed.set_footer(
                text="AbbyBot",  
                icon_url=abbyBot_guild_icon  
            )

        # Get logs_channel ID
        cursor.execute("SELECT logs_channel FROM server_settings WHERE guild_id = %s", (guild_id,))
        default_channel = cursor.fetchone()

        if default_channel is not None and default_channel[0] is not None:
            logs_channel = self.bot.get_channel(default_channel[0])  # Get the TextChannel object

            if logs_channel is not None:
                await logs_channel.send(embed=embed)

        # Close db
        cursor.close()
        db.close()
