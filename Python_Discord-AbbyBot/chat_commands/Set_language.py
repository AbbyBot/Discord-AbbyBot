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
        discord.app_commands.Choice(name="English", value=1),  # 1 en
        discord.app_commands.Choice(name="Español", value=2)  # 2 es
    ])
    async def set_language(self, interaction: discord.Interaction, language: int):

        # Connect to db using MySQL
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

        # Get server's bot language
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        current_language_id = cursor.fetchone()[0]  # We assume that there is always an outcome

            # Check if user has admin permission
        if not interaction.user.guild_permissions.administrator:
            if current_language_id == 1:
                await interaction.response.send_message("You do not have permission to change the AbbyBot's language.", ephemeral=True)
                return
            if current_language_id == 2:
                await interaction.response.send_message("No tienes permiso para cambiar el idioma de AbbyBot.", ephemeral=True)
                return

        # Confirm to user
        if current_language_id == 1:
            await interaction.response.send_message("My language has been set to English.", ephemeral=False)
        elif current_language_id == 2:
            await interaction.response.send_message("Mi idioma ha sido cambiado a Español.", ephemeral=False)

        # Close db connection
        cursor.close()
        db.close()

# Add cog command
async def setup(bot):
    await bot.add_cog(SetLanguage(bot))
