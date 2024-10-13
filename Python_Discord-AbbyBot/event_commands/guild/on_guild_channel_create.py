import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
from utils.utils import get_bot_avatar
from datetime import datetime

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


        bot_id = 1028065784016142398  # AbbyBot ID
        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

        if language_id == 1:
                
                now = datetime.now()
                english_datetime = now.strftime("%m/%d/%Y %H:%M:%S")
                embed = discord.Embed(
                    title="Channel created",
                    description="A new channel has been created:",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=bot_avatar_url)
                embed.add_field(name="Date and time", value=english_datetime, inline=True)
                embed.add_field(name="Channel name", value=f"{guild.name}")
                embed.set_footer(text="AbbyBot", icon_url=bot_avatar_url)


        elif language_id == 2:
                
                now = datetime.now()
                spanish_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
                embed = discord.Embed(
                    title="Canal creado",
                    description="Un nuevo canal ha sido creado:",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=bot_avatar_url)
                embed.add_field(name="Fecha y hora", value=spanish_datetime, inline=True)
                embed.add_field(name="Nombre del canal", value=f"{guild.name}")
                embed.set_footer(text="AbbyBot", icon_url=bot_avatar_url)

        # Get logs_channel ID
        cursor.execute("select logs_channel from server_settings where guild_id = %s", (guild_id,))
        default_channel = cursor.fetchone()

        if default_channel is not None and default_channel[0] is not None:
            logs_channel = self.bot.get_channel(default_channel[0])  # Get the TextChannel object

            if logs_channel is not None:
                await logs_channel.send(embed=embed)

        # Close bd
        cursor.close()
        db.close()

