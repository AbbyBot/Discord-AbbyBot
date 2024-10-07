import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables dotenv
load_dotenv()

class ChannelCreateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event: on_guild_channel_delete
    @commands.Cog.listener()
    async def on_guild_channel_create(self, guild: discord.Guild):
        # Load dotenv variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        guild_id = guild.guild.id

        # Check if the server has activated_logs = 1
        cursor.execute("select activated_logs from server_settings where guild_id = %s", (guild_id,))
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

        # Check language
        language_id = result[0]
        if language_id == 1:
            response_message = f"A new guild channel named **{guild.name}** has been created in this server."
        elif language_id == 2:
            response_message = f"Se ha creado un nuevo canal llamado **{guild.name}** en este servidor."

        # Get logs_channel ID
        cursor.execute("select logs_channel from server_settings where guild_id = %s", (guild_id,))
        default_channel = cursor.fetchone()

        if default_channel is not None and default_channel[0] is not None:
            logs_channel = self.bot.get_channel(default_channel[0])  # Get the TextChannel object

            if logs_channel is not None:
                await logs_channel.send(response_message)


        # Close bd
        cursor.close()
        db.close()

