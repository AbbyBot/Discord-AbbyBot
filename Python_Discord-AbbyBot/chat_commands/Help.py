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

            # if serrver are not registered, send error message

            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # Get server language
        language_code = result[0]

        # Commands and description Query
        cursor.execute("SELECT command_code, command_description FROM help WHERE language_code = %s", (language_code,))
        commands_help = cursor.fetchall()


 # Create embed
        embed = discord.Embed(
            title="Help",
            description="Here are the available commands:",
            color=discord.Color.from_rgb(145, 61, 33)  # Abbybot's color
        )

        # Add commands and descriptions
        for command_code, command_description in commands_help:
            embed.add_field(name=command_code, value=command_description, inline=False)

        # Abbybot's pfp.png file
        image_path = "abbybot.png"

        # Load image like discord file
        file = discord.File(image_path, filename="abbybot.png")

        # Add img to embed
        embed.set_image(url="attachment://abbybot.png")

        # Send message and image
        await interaction.response.send_message(embed=embed, file=file)

        # Close dba connection
        cursor.close()
        db.close()

async def setup(bot):
    await bot.add_cog(Help(bot))
