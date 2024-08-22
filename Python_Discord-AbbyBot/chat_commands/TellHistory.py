import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class TellHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tell_history", description="Let AbbyBot tell you something!")
    @app_commands.choices(
        category=[
            app_commands.Choice(name="About Her", value="About Her"),
            app_commands.Choice(name="Lore", value="Lore"),
            app_commands.Choice(name="Advice", value="Advice"),
        ]
    )
    async def tell_history(self, interaction: discord.Interaction, category: app_commands.Choice[str]):

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

        # Get the language_id of the server
        language_id = result[0]

        # Query to get a random dialogue from the selected category and the server's language
        cursor.execute("""
            SELECT d.message FROM dialogues d
            JOIN categories c ON d.category_id = c.id
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
            color=discord.Color.from_rgb(145, 61, 33)  # Abbybot's color
        )

        # Send message
        await interaction.response.send_message(embed=embed)

        # Close DB connection
      
