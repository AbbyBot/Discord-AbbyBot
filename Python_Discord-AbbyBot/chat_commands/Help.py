import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Do you have any questions?")
    async def help(self, interaction: discord.Interaction):

        # Connect to database with dotenv variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

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
        language_id = result[0]  # Aquí obtenemos el ID del lenguaje correctamente

        # Commands and description Query
        cursor.execute("SELECT command_code, command_description FROM help WHERE language_code = (SELECT language_code FROM languages WHERE id = %s)", (language_id,))
        commands_help = cursor.fetchall()

        # Validate the language, title, and change the description as appropriate
        if language_id == 1:
            description_title = 'Help'
            description_text = "Here are the available commands:"
        elif language_id == 2:
            description_title = 'Ayuda'
            description_text = "Aquí están los comandos disponibles:"
        else:
            description_title = 'Help'
            description_text = "Here are the available commands:"  # English default

        # Create embed
        embed = discord.Embed(
            title=description_title,
            description=description_text,
            color=discord.Color.from_rgb(145, 61, 33)  # Abbybot's color
        )

        # Add commands and descriptions
        for command_code, command_description in commands_help:
            embed.add_field(name=command_code, value=command_description, inline=False)

        
        # Validate the language, different img
        if language_id == 1:
            # Abbybot's pfp.png file (English)
            image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "help", "abbybot-help_en.png")
        elif language_id == 2:
            # Abbybot's pfp.png file (Spanish)
            image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "help", "abbybot-help_es.png")
        else:
            # Abbybot's pfp.png file (English DEFAULT)
            image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "help", "abbybot-help_en.png")

        # Load image like discord file
        file = discord.File(image_path, filename="abbybot.png")

        # Add img to embed
        embed.set_image(url="attachment://abbybot.png")

        # Send message and image
        await interaction.response.send_message(embed=embed, file=file)

        # Close db connection
        cursor.close()
        db.close()

# Add cog command
async def setup(bot):
    await bot.add_cog(Help(bot))
