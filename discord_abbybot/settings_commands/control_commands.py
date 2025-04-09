import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class ControlGroup(commands.GroupCog, name="control"):
    def __init__(self, bot):
        self.bot = bot

    async def get_guild_language(self, guild_id, cursor):
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    async def check_admin_permission(self, interaction, language_id):
        if not interaction.user.guild_permissions.administrator:
            if language_id == 1:
                await interaction.response.send_message("You do not have permission to activate/deactivate the AbbyBot settings.", ephemeral=True)
            elif language_id == 2:
                await interaction.response.send_message("No tienes permiso para activar/desactivar la configuración de AbbyBot.", ephemeral=True)
            return False
        return True

    # Common method to update settings
    async def update_setting(self, interaction: discord.Interaction, setting_column: str, value: int):
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        guild_id = interaction.guild_id

        # Check if guild are registered
        language_id = await self.get_guild_language(guild_id, cursor)
        if language_id is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # Check if user are admin
        if not await self.check_admin_permission(interaction, language_id):
            cursor.close()
            db.close()
            return

        # Update value in db
        cursor.execute(f"UPDATE server_settings SET {setting_column} = %s WHERE guild_id = %s", (value, guild_id))
        db.commit()

        # Confirmation of the action taken with language support
        if setting_column == "activated_events":
            if language_id == 1:  # English
                action = "automatic events of AbbyBot"
            elif language_id == 2:  # Spansih
                action = "eventos automáticos de AbbyBot"
        elif setting_column == "activated_logs":
            if language_id == 1:  # English
                action = "log system of AbbyBot"
            elif language_id == 2:  # Spanish
                action = "sistema de logs de AbbyBot"
        elif setting_column == "activated_birthday":
            if language_id == 1:  # English
                action = "birthday system of AbbyBot"
            elif language_id == 2:  # Spanish
                action = "sistema de cumpleaños de AbbyBot"
        else:
            if language_id == 1:  # English
                action = "settings of AbbyBot"
            elif language_id == 2:  # Spanish
                action = "configuración de AbbyBot"

        # Language-dependent response
        if value == 1:  # Activated
            if language_id == 1:
                await interaction.response.send_message(f"{action} has been activated.", ephemeral=False)
            elif language_id == 2:
                await interaction.response.send_message(f"se ha activado el {action}.", ephemeral=False)
        elif value == 0:  # Disabled
            if language_id == 1:
                await interaction.response.send_message(f"{action} has been deactivated.", ephemeral=False)
            elif language_id == 2:
                await interaction.response.send_message(f"Se ha desactivado el {action}.", ephemeral=False)

        # Close db connection
        cursor.close()
        db.close()

    # Subcommand to activate/deactivate events
    @app_commands.command(name="events", description="Activate or deactivate AbbyBot events.")
    @app_commands.choices(activated_events=[
        discord.app_commands.Choice(name="Enable", value=1),  
        discord.app_commands.Choice(name="Disable", value=0)  
    ])
    async def control_events(self, interaction: discord.Interaction, activated_events: int):
        await self.update_setting(interaction, "activated_events", activated_events)

    # Subcommand to activate/deactivate logs
    @app_commands.command(name="logs", description="Activate or deactivate AbbyBot logs.")
    @app_commands.choices(activated_logs=[
        discord.app_commands.Choice(name="Enable", value=1),  
        discord.app_commands.Choice(name="Disable", value=0)  
    ])
    async def control_logs(self, interaction: discord.Interaction, activated_logs: int):
        await self.update_setting(interaction, "activated_logs", activated_logs)

    # Subcommand to activate/deactivate birthdays
    @app_commands.command(name="birthday", description="Activate or deactivate AbbyBot birthday messages.")
    @app_commands.choices(activated_birthday=[
        discord.app_commands.Choice(name="Enable", value=1),  
        discord.app_commands.Choice(name="Disable", value=0)  
    ])
    async def control_birthday(self, interaction: discord.Interaction, activated_birthday: int):
        await self.update_setting(interaction, "activated_birthday", activated_birthday)
