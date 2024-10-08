import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os
from embeds.embeds import account_inactive_embed

from utils.utils import get_bot_avatar 




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

        # Get guild_id and user_id from the interaction
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        # Check if server is registered
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        # Check if the user is active (is_active = 1) or inactive (is_active = 0)
        cursor.execute("SELECT is_active FROM user_profile WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("User not found in the database.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # If the user is inactive (is_active = 0), send an embed in DM and exit
        is_active = result[0]
        if is_active == 0:
            try:
                # Get the embed and file
                embed, file = account_inactive_embed()

                # Send the embed and the file as DM
                await interaction.user.send(embed=embed, file=file)
                
                print(f"User {interaction.user} is inactive and notified.")
            except discord.Forbidden:
                print(f"Could not send DM to {interaction.user}. They may have DMs disabled.")

            await interaction.response.send_message("Request Rejected: Your account has been listed as **inactive** in the AbbyBot system, please check your DM.", ephemeral=True)

            cursor.close()
            db.close()
            return

        # Query to check the server's language setting (obligatory field)
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return
        
        # Get server language
        
        language_id = result[0]  # Get language ID

        # Commands and description Query
        cursor.execute("SELECT command_code, command_description FROM help WHERE language_id = %s", (language_id,))
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

        bot_id = 1028065784016142398  # AbbyBot ID


        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

        embed.set_footer(text="AbbyBot",  icon_url=bot_avatar_url)

        # Send message and image
        await interaction.response.send_message(embed=embed, file=file)

        # Close db connection
        cursor.close()
        db.close()

