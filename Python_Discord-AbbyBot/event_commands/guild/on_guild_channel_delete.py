import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
from utils.utils import get_bot_avatar
from datetime import datetime

# Load dotenv variables
load_dotenv()

class ChannelDeleteEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event: on_guild_channel_delete
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.TextChannel):
        # Load dotenv variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        guild_id = channel.guild.id  # Get server ID

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

        # Get the audit logs to find who deleted the channel
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:  # Check if the deleted channel matches
                user = entry.user  # The user who deleted the channel

        # Check language and create response message
        language_id = result[0]

        # Get server icon from db
        cursor.execute("SELECT guild_icon_url FROM server_settings WHERE guild_id = %s", (guild_id,))
        bot_avatar_url = cursor.fetchone()

        # Get AbbyBot ID and icon
        bot_id = 1028065784016142398  # AbbyBot ID
        abbyBot_guild_icon = await get_bot_avatar(self.bot, bot_id)


        if bot_avatar_url is None or not bot_avatar_url[0].startswith("http"):
            
            bot_avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  
        else:
            bot_avatar_url = bot_avatar_url[0]

        now = datetime.now()
        if language_id == 1:

            english_datetime = now.strftime("%m/%d/%Y %H:%M:%S")
            embed = discord.Embed(
                title="Channel deleted",
                description="A channel has been deleted:",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=bot_avatar_url)
            embed.add_field(name="Date and time", value=english_datetime, inline=True)
            embed.add_field(name="Channel name", value=f"{channel.name}", inline=True)
            embed.add_field(name="Who deleted it?", value=f"{user.name}", inline=True)
            embed.set_footer(text="AbbyBot", icon_url=abbyBot_guild_icon)

        elif language_id == 2:

            spanish_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
            embed = discord.Embed(
                title="Canal eliminado",
                description="Un canal ha sido eliminado:",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=bot_avatar_url)
            embed.add_field(name="Fecha y hora", value=spanish_datetime, inline=True)
            embed.add_field(name="Nombre del canal", value=f"{channel.name}", inline=True)
            embed.add_field(name="Quién lo eliminó?", value=f"{user.name}", inline=True)
            embed.set_footer(text="AbbyBot", icon_url=abbyBot_guild_icon)

        # Get logs_channel ID
        cursor.execute("SELECT logs_channel FROM server_settings WHERE guild_id = %s", (guild_id,))
        default_channel = cursor.fetchone()

        if default_channel is not None and default_channel[0] is not None:
            logs_channel = self.bot.get_channel(default_channel[0])  # Get the TextChannel object

            if logs_channel is not None:
                await logs_channel.send(embed=embed)

        # Close bd
        cursor.close()
        db.close()
