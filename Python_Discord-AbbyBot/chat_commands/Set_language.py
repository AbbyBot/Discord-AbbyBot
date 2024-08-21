import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class SetLanguage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_language", description="Set the language for this server.")
    @app_commands.choices(language=[
        discord.app_commands.Choice(name="English", value="en"),
        discord.app_commands.Choice(name="Español", value="es")
    ])
    async def set_language(self, interaction: discord.Interaction, language: str):
        # Check if user have admin permisison
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to change the language.", ephemeral=True)
            return

        # Connect db using MySQL
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        guild_id = interaction.guild_id

        # Update language in database
        cursor.execute("UPDATE server_settings SET guild_language = %s WHERE guild_id = %s", (language, guild_id))
        db.commit()

        # Obtener el idioma actual del servidor
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        current_language = cursor.fetchone()[0]  # Suponemos que siempre existe un resultado

        # Confirm to user
        if language == 'en':
            await interaction.response.send_message("The language has been set to English.", ephemeral=True)
        elif language == 'es':
            await interaction.response.send_message("El idioma ha sido cambiado a Español.", ephemeral=True)

        # Close db connection
        cursor.close()
        db.close()

# Add cog command
async def setup(bot):
    await bot.add_cog(SetLanguage(bot))
