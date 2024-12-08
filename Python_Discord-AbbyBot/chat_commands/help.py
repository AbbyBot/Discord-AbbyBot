import discord
from discord.ext import commands
from discord import app_commands
from utils.db_utils import get_db_connection
import os

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def autocomplete_category(self, interaction: discord.Interaction, current: str):
        db, cursor = get_db_connection()

        # Query categories in the database, filtering by current text
        cursor.execute(
            "SELECT id, category_name FROM help_categories WHERE category_name LIKE %s",
            (f"%{current}%",)
        )
        categories = cursor.fetchall()

        # Close database connection
        cursor.close()
        db.close()

        # Return categories for autocomplete
        return [app_commands.Choice(name=cat[1], value=str(cat[0])) for cat in categories]

    @app_commands.command(name="help", description="Do you have any questions?")
    @app_commands.autocomplete(category=autocomplete_category)  # Autocomplete for category
    async def help(self, interaction: discord.Interaction, category: str):
        db, cursor = get_db_connection()

        # Get guild_id and user_id from the command
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        # Check if the server is registered and get the language
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        language_id = result[0]

        # Query commands related to the category
        cursor.execute(
            "SELECT command_code, command_description FROM help WHERE language_id = %s AND category_id = %s",
            (language_id, category)
        )
        commands_help = cursor.fetchall()

        # Define title and description text according to language
        if language_id == 1:
            description_title = '📖 AbbyBot Help Center'
            description_text = "✨ Explore the available commands below:"
        elif language_id == 2:
            description_title = '📖 Centro de Ayuda de AbbyBot'
            description_text = "✨ Explora los comandos disponibles a continuación:"
        else:
            description_title = '📖 AbbyBot Help Center'
            description_text = "✨ Explore the available commands below:"

        # Create embed
        embed = discord.Embed(
            title=description_title,
            description=description_text,
            color=discord.Color.from_rgb(145, 61, 33)  # Abbybot color
        )

        # Add commands and descriptions to the embed
        if commands_help:
            for command_code, command_description in commands_help:
                embed.add_field(name=f"🔹 {command_code}", value=command_description, inline=False)
        else:
            embed.description = "❌ No commands found for this category."

        # Set image as thumbnail (PFP-style)
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "profile_emotes", "abbybot_laptop.png")
        file = discord.File(image_path, filename="abbybot_thumbnail.png")
        embed.set_thumbnail(url="attachment://abbybot_thumbnail.png")

        
        footer_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "abbybot.png")
        footer_file = discord.File(footer_image_path, filename="abbybot.png")
        embed.set_footer(text="AbbyBot • Your Discord Ally", icon_url="attachment://abbybot.png")

        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Command List", url="https://abbybotproject.com/commands", style=discord.ButtonStyle.link))
        view.add_item(discord.ui.Button(label="Website", url="https://abbybotproject.com", style=discord.ButtonStyle.link))

        
        await interaction.response.send_message(embed=embed, files=[file, footer_file], view=view)

        cursor.close()
        db.close()
