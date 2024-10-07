import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os
from embeds.embeds import account_inactive_embed # import embed system

# Load dotenv variables
load_dotenv()

# Define supported languages
supported_languages = {
    'python': 'python',
    'javascript': 'javascript',
    'java': 'java',
    'c': 'c',
    'cpp': 'cpp',
    'html': 'html',
    'css': 'css',
    'json': 'json',
    'bash': 'bash',
    'yaml': 'yaml',
    'xml': 'xml',
    'sql': 'sql',
    'ruby': 'ruby',
    'php': 'php',
    'go': 'go',
    'rust': 'rust',
    'kotlin': 'kotlin',
    'swift': 'swift',
    'plaintext': ''  # For plain text, no syntax highlighting
}

class Code(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="code", description="Send formatted code with language support")
    @app_commands.describe(language="Programming language for syntax highlighting", code="Code to format and send")
    async def command_name(self, interaction: discord.Interaction, code: str, language: str = "plaintext"):
        # Connect to the database using environment variables
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

        # Check if the user is active (is_active = 1) or inactive (is_active = 0)
        cursor.execute("SELECT is_active FROM user_profile WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("User not found in the database.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # If the user is inactive (banned), send an embed in DM and exit
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
            
            cursor.close()
            db.close()
            await interaction.response.send_message("Request Rejected: Your account has been listed as **inactive** in the AbbyBot system, please check your DM.", ephemeral=True)
            return

        # Validate the selected language or default to plaintext
        language = supported_languages.get(language.lower(), "")

        # Format the code with the appropriate language for syntax highlighting
        formatted_code = f"```{language}\n{code}\n```"

        # Send the response
        await interaction.response.defer()  # Defer the response temporarily while processing
        await interaction.followup.send(formatted_code)

        # Close the database connection
        cursor.close()
        db.close()
