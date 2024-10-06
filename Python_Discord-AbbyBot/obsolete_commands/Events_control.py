import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class EventsControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="events_control", description="Set the language for this server.")
    @app_commands.choices(activated_events=[
        discord.app_commands.Choice(name="Enable", value=1),  
        discord.app_commands.Choice(name="Disable", value=0)  
    ])
    async def set_language(self, interaction: discord.Interaction, activated_events: int):


        # Connect to db using MySQL
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get server ID
        guild_id = interaction.guild_id

        # Check if server is registered
        guild_id = interaction.guild_id
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            # if server is not registered, send error message
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # Get server language
        language_id = result[0]  # Get language ID

        # Check if user has admin permission
        if not interaction.user.guild_permissions.administrator:
            if language_id == 1:
                await interaction.response.send_message("You do not have permission to activate/deactivate the AbbyBot Events.", ephemeral=True)
                return
            if language_id == 2:   
                await interaction.response.send_message("No tienes permiso para activar/desactivar los eventos de AbbyBot.", ephemeral=True)
                return

        # Get activated_events value in server
        cursor.execute("SELECT activated_events FROM server_settings WHERE guild_id = %s", (guild_id,))
        activated_events_value = cursor.fetchone()

        # Update activated_events with the selected value
        cursor.execute("UPDATE server_settings SET activated_events = %s WHERE guild_id = %s", (activated_events, guild_id))
        db.commit()

        # Confirm to user
        if activated_events == 1:
            if language_id == 1:
                await interaction.response.send_message("Abbybot events have been activated.", ephemeral=False)
            if language_id == 2:
                await interaction.response.send_message("Se han activado los eventos de Abbybot.", ephemeral=False)
        elif activated_events == 0:
            if language_id == 1:
                await interaction.response.send_message("Abbybot events have been deactivated.", ephemeral=False)
            if language_id == 2:
                await interaction.response.send_message("Se han desactivado los eventos de Abbybot.", ephemeral=False)

        # Close db connection
        cursor.close()
        db.close()

# Add cog command
async def setup(bot):
    await bot.add_cog(EventsControl(bot))
