import discord
from discord.ext import commands
from discord import app_commands
from utils.db_utils import get_db_connection

class TellGroup(commands.GroupCog, name="tell"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name="story", description="Let AbbyBot tell you a story!")
    @app_commands.choices(
        category=[
            app_commands.Choice(name="About AbbyBot", value="About Her"),
            app_commands.Choice(name="Her Lore", value="Lore"),
        ]
    )
    async def stories(self, interaction: discord.Interaction, category: app_commands.Choice[str]):

        db, cursor = get_db_connection()

        # Check if server is registered
        guild_id = interaction.guild_id
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            # If server is not registered, send error message
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # Get the language_id of the server
        language_id = result[0]

        # Query to get a random dialogue from the selected category and the server's language
        cursor.execute("""
            SELECT d.message FROM dialogues d
            JOIN story_categories c ON d.category_id = c.id
            WHERE c.category = %s AND d.language_id = %s
            ORDER BY RAND() LIMIT 1;
        """, (category.value, language_id))
        dialogue = cursor.fetchone()

        if dialogue is None:
            # If no dialogue is found, send an error message based on the language_id
            if language_id == 1:  # English
                error_message = f"Sorry, I don't have anything to say in the {category.value} category."
            elif language_id == 2:  # Spanish
                error_message = f"Lo siento, no tengo nada que decir en la categoría {category.value}."
            else:
                error_message = f"Sorry, I don't have anything to say in the {category.value} category."  # Default to English

            await interaction.response.send_message(error_message, ephemeral=True)
            cursor.close()
            db.close()
            return

        # Create and send the embed with the dialogue
        embed = discord.Embed(
            title=category.value,
            description=dialogue[0],  # Fetch the first column, which is the message
            color=discord.Color.random()
        )

        # Send message
        await interaction.response.send_message(embed=embed)

