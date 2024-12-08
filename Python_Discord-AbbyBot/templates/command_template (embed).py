import discord
from discord.ext import commands
from discord import app_commands
from utils.db_utils import get_db_connection
import os

class TemplateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def autocomplete_example(self, interaction: discord.Interaction, current: str):
        db, cursor = get_db_connection()

        # Query example data from the database, filtering by current text
        cursor.execute(
            "SELECT id, example_name FROM example_table WHERE example_name LIKE %s",
            (f"%{current}%",)
        )
        examples = cursor.fetchall()

        # Close database connection
        cursor.close()
        db.close()

        # Return autocompletion choices
        return [app_commands.Choice(name=example[1], value=str(example[0])) for example in examples]

    @app_commands.command(name="template", description="A generic template command")
    @app_commands.autocomplete(example=autocomplete_example)  # Autocomplete example
    async def template_command(self, interaction: discord.Interaction, example: str):
        db, cursor = get_db_connection()

        # Example: Fetch guild and user details
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        # Example: Check server registration in the database
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        language_id = result[0]

        # Example: Query data related to the example parameter
        cursor.execute(
            "SELECT code, description FROM example_table WHERE language_id = %s AND example_id = %s",
            (language_id, example)
        )
        example_data = cursor.fetchall()

        # Define titles and descriptions based on the language
        if language_id == 1:
            title = "📖 Template Command Center"
            description = "✨ Explore the following data:"
        elif language_id == 2:
            title = "📖 Centro de Comandos de Plantilla"
            description = "✨ Explora los datos a continuación:"
        else:
            title = "📖 Template Command Center"
            description = "✨ Explore the following data:"

        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()  # Adjust color as needed
        )

        # Add data fields to the embed
        if example_data:
            for code, desc in example_data:
                embed.add_field(name=f"🔹 {code}", value=desc, inline=False)
        else:
            embed.description = "❌ No data found for this example."

        # Example: Add thumbnail and footer images
        image_path = os.path.join(os.path.dirname(__file__), "images", "example_thumbnail.png")
        file = discord.File(image_path, filename="example_thumbnail.png")
        embed.set_thumbnail(url="attachment://example_thumbnail.png")

        footer_path = os.path.join(os.path.dirname(__file__), "images", "example_footer.png")
        footer_file = discord.File(footer_path, filename="example_footer.png")
        embed.set_footer(text="Template Bot • Your Discord Ally", icon_url="attachment://example_footer.png")

        # Example: Add buttons to the response
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Visit Website", url="https://example.com", style=discord.ButtonStyle.link))
        view.add_item(discord.ui.Button(label="Support", url="https://example.com/support", style=discord.ButtonStyle.link))

        # Send response
        await interaction.response.send_message(embed=embed, files=[file, footer_file], view=view)

        cursor.close()
        db.close()


# Cog setup
async def setup(bot):
    await bot.add_cog(TemplateCommand(bot))
