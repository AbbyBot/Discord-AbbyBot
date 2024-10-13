import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
from utils.utils import get_bot_avatar
from datetime import datetime

# Load dotenv variables
load_dotenv()

class MemberUpdateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event: on_member_update
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
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

        # Compare changes
        changes = []

        # Handle nickname changes
        if before.nick != after.nick:
            before_nick = before.nick if before.nick is not None else before.name  # Show username if no previous nickname
            after_nick = after.nick if after.nick is not None else after.name  # Show username if no current nickname

            if language_id == 1:
                changes.append(f"Nickname changed from **{before_nick}** to **{after_nick}**.")
            elif language_id == 2:
                changes.append(f"Apodo cambiado de **{before_nick}** a **{after_nick}**.")

            # Get user_id from the user_profile using Discord's member ID (after.id)
            cursor.execute("""
                SELECT ds.user_profile_id
                FROM dashboard ds
                JOIN user_profile up ON ds.user_profile_id = up.id
                WHERE ds.guild_id = %s AND up.user_id = %s;
            """, (guild_id, after.id))
            user_profile = cursor.fetchone()

            # Check if user_profile was found
            if user_profile is not None:
                user_id = user_profile[0]
                
                # Now that you have the user_id, you can proceed with updating the nickname
                cursor.execute("""
                    UPDATE dashboard 
                    SET user_server_nickname = %s 
                    WHERE user_profile_id = %s AND guild_id = %s
                """, (after_nick, user_id, guild_id))
                db.commit()

        # Handle role changes (already implemented)
        if before.roles != after.roles:
            roles_before = set(before.roles)
            roles_after = set(after.roles)

            added_roles = roles_after - roles_before
            if added_roles:
                for role in added_roles:
                    if language_id == 1:
                        changes.append(f"Role added: **{role.name}**.")
                    elif language_id == 2:
                        changes.append(f"Rol añadido: **{role.name}**.")

            removed_roles = roles_before - roles_after
            if removed_roles:
                for role in removed_roles:
                    if language_id == 1:
                        changes.append(f"Role removed: **{role.name}**.")
                    elif language_id == 2:
                        changes.append(f"Rol eliminado: **{role.name}**.")

        # If there are changes, create an embed message
        if changes:
            now = datetime.now()

            if language_id == 1:  # English
                english_datetime = now.strftime("%m/%d/%Y %H:%M:%S")
                embed = discord.Embed(
                    title="Member Updated",
                    description="Changes in member attributes:",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=bot_avatar_url)
                embed.add_field(name="Date and time", value=english_datetime, inline=True)
                embed.add_field(name="Changes", value="\n".join(changes), inline=False)
                embed.set_footer(text="AbbyBot", icon_url=bot_avatar_url)

            elif language_id == 2:  # Spanish
                spanish_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
                embed = discord.Embed(
                    title="Miembro Actualizado",
                    description="Cambios en los atributos del miembro:",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=bot_avatar_url)
                embed.add_field(name="Fecha y hora", value=spanish_datetime, inline=True)
                embed.add_field(name="Cambios", value="\n.join(changes)", inline=False)
                embed.set_footer(text="AbbyBot", icon_url=bot_avatar_url)

            # Get logs_channel ID
            cursor.execute("SELECT logs_channel FROM server_settings WHERE guild_id = %s", (guild_id,))
            default_channel = cursor.fetchone()

            if default_channel is not None and default_channel[0] is not None:
                logs_channel = self.bot.get_channel(default_channel[0])

                if logs_channel is not None:
                    await logs_channel.send(embed=embed)

        # Close db connection
        cursor.close()
        db.close()
