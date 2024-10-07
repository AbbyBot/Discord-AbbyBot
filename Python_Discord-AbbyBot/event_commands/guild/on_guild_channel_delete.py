import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

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

        guild_id = channel.guild.id  # Here we get the server ID through the channel

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
        if language_id == 1:
            response_message = f"The channel **{channel.name}** has been deleted by **{user.name}**."
        elif language_id == 2:
            response_message = f"El canal **{channel.name}** ha sido eliminado por **{user.name}**."

        # Get logs_channel ID
        cursor.execute("SELECT logs_channel FROM server_settings WHERE guild_id = %s", (guild_id,))
        default_channel = cursor.fetchone()

        if default_channel is not None and default_channel[0] is not None:
            logs_channel = self.bot.get_channel(default_channel[0])  # Get the TextChannel object

            if logs_channel is not None:
                await logs_channel.send(response_message)

        # Close bd
        cursor.close()
        db.close()
