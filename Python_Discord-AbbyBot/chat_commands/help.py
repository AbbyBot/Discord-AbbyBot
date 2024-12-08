import discord
from discord.ext import commands
from discord import app_commands
import os
from embeds.embeds import account_inactive_embed
from utils.utils import get_bot_avatar 
from utils.db_utils import get_db_connection


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Do you have any questions?")
    async def help(self, interaction: discord.Interaction):

        db, cursor = get_db_connection()

        # Get guild_id and user_id from the interaction
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        # Check if server is registered
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

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

