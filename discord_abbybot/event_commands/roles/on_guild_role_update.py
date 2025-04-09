import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
from utils.utils import get_bot_avatar
from datetime import datetime

# Load dotenv variables
load_dotenv()

class RoleUpdateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event: on_guild_role_update
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        # Load dotenv variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        guild_id = after.guild.id

        # Check if the logs are activated
        cursor.execute("SELECT activated_logs FROM server_settings WHERE guild_id = %s", (guild_id,))
        logs_result = cursor.fetchone()

        if logs_result is None or logs_result[0] == 0:
            # If logs are not activated or there is no result, do nothing
            cursor.close()
            db.close()
            return

        # Check guild language
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            # If the server is not registered, do nothing
            cursor.close()
            db.close()
            return

        language_id = result[0]
        bot_id = 1028065784016142398  # AbbyBot ID
        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

        # Compare role attributes and generate changes
        changes = []

        if before.name != after.name:
            changes.append(f"Name changed from **{before.name}** to **{after.name}**." if language_id == 1 else f"Nombre cambiado de **{before.name}** a **{after.name}**.")
        
        if before.permissions != after.permissions:
            changes.append(f"Permissions updated.")
        
        if before.color != after.color:
            changes.append(f"Color changed from **{before.color}** to **{after.color}**." if language_id == 1 else f"Color cambiado de **{before.color}** a **{after.color}**.")

        # If there are changes, create an embed message
        if changes:
            now = datetime.now()

            if language_id == 1:  # English
                english_datetime = now.strftime("%m/%d/%Y %H:%M:%S")
                embed = discord.Embed(
                    title="Role Updated",
                    description=f"The role **{before.name}** has been updated.",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=bot_avatar_url)
                embed.add_field(name="Date and time", value=english_datetime, inline=True)
                embed.add_field(name="Changes", value="\n".join(changes), inline=False)
                embed.set_footer(text="AbbyBot", icon_url=bot_avatar_url)

            elif language_id == 2:  # Spanish
                spanish_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
                embed = discord.Embed(
                    title="Rol Actualizado",
                    description=f"El rol **{before.name}** ha sido actualizado.",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=bot_avatar_url)
                embed.add_field(name="Fecha y hora", value=spanish_datetime, inline=True)
                embed.add_field(name="Cambios", value="\n".join(changes), inline=False)
                embed.set_footer(text="AbbyBot", icon_url=bot_avatar_url)

            # Get logs_channel ID
            cursor.execute("SELECT logs_channel FROM server_settings WHERE guild_id = %s", (guild_id,))
            default_channel = cursor.fetchone()

            if default_channel is not None and default_channel[0] is not None:
                logs_channel = self.bot.get_channel(default_channel[0])  # Get the TextChannel object

                if logs_channel is not None:
                    await logs_channel.send(embed=embed)

        # Close db connection
        cursor.close()
        db.close()
