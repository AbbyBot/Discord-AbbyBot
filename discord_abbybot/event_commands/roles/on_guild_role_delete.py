import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from utils.utils import get_bot_avatar
from datetime import datetime
from utils.db_utils import get_db_connection

# Cargar variables dotenv
load_dotenv()

class RoleDeleteEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event: on_guild_role_delete
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        # Connect to database with dotenv variables
        db, cursor = get_db_connection()

        guild_id = role.guild.id

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

        # Get the audit logs to find who deleted the role
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if entry.target.id == role.id:  # Check if the deleted role matches
                user = entry.user  # The user who deleted the role

        # Create embed message
        language_id = result[0]

        bot_id = 1028065784016142398  # AbbyBot ID

        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

        # Load dotenv footer text 
        footer_text_en = os.getenv("FOOTER_TEXT_EN", "AbbyBot")
        footer_text_es = os.getenv("FOOTER_TEXT_ES", "AbbyBot")

        if language_id == 1:
            now = datetime.now()
            english_datetime = now.strftime("%m/%d/%Y %H:%M:%S")
            embed = discord.Embed(
                title="Role Deleted",
                description=f"A role named has been deleted in this server.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=bot_avatar_url)
            embed.add_field(name="Date and time", value=english_datetime, inline=True)
            embed.add_field(name="Role name", value=f"{role.name}", inline=True)
            embed.set_footer(
                text=footer_text_en,  
                icon_url=bot_avatar_url  
            )


        elif language_id == 2:
            now = datetime.now()
            spanish_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
            embed = discord.Embed(
                title="Rol Eliminado",
                description=f"Se ha eliminado un rol llamado {role.name} en este servidor.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=bot_avatar_url)
            embed.add_field(name="Fecha y hora", value=spanish_datetime, inline=True)
            embed.add_field(name="Nombre del rol", value=f"{role.name}", inline=True)
            embed.set_footer(
                text=footer_text_es,  
                icon_url=bot_avatar_url  
            )

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
