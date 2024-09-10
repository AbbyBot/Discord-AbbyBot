import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class SetPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_prefix", description="Change AbbyBot's prefix")
    async def set_language(self, interaction: discord.Interaction, text: str = None):

        # Connect to db using MySQL
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        guild_id = interaction.guild_id


        # Get server's bot language
        cursor.execute("SELECT guild_language, prefix FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()  # Fetch both language and current prefix
        current_language_id = result[0]  # We assume that there is always an outcome
        current_prefix = result[1]

            # Check if user has admin permission
        if not interaction.user.guild_permissions.administrator:
            if current_language_id == 1:
                await interaction.response.send_message("You do not have permission to change the AbbyBot's prefix.", ephemeral=True)
                return
            if current_language_id == 2:
                await interaction.response.send_message("No tienes permiso para cambiar el prefijo de AbbyBot.", ephemeral=True)
                return
            
        if text is None:
            if language_id == 1:
                await interaction.followup.send("Please provide the prefix for AbbyBot.")
                return
            if language_id == 2:
                await interaction.followup.send("Por favor proporcione el prefijo para AbbyBot.")
                return

        #Update prefix
        cursor.execute("UPDATE server_settings SET prefix = %s WHERE guild_id = %s", (text, guild_id))
        db.commit()


        # Confirm to user
        if current_language_id == 1:
            await interaction.response.send_message(f"My prefix has been changed to {text}.", ephemeral=False)
        elif current_language_id == 2:
            await interaction.response.send_message(f"Mi prefijo ha sido cambiado a {text}.", ephemeral=False)

        # Close db connection
        cursor.close()
        db.close()

# Add cog command
async def setup(bot):
    await bot.add_cog(SetPrefix(bot))
