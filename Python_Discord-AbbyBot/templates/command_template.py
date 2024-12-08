import discord
from discord.ext import commands
from discord import app_commands
from utils.db_utils import get_db_connection

class TemplateCommandPlain(commands.Cog):
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

    @app_commands.command(name="template", description="A plain text template command")
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
            await interaction.response.send_message("⚠️ This server is not registered. Please contact the admin.", ephemeral=True)
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
            description = "✨ Here is the requested information:"
        elif language_id == 2:
            title = "📖 Centro de Comandos de Plantilla"
            description = "✨ Aquí está la información solicitada:"
        else:
            title = "📖 Template Command Center"
            description = "✨ Here is the requested information:"

        # Format the response as plain text
        response = f"**{title}**\n{description}\n\n"

        # Add the data to the response
        if example_data:
            for code, desc in example_data:
                response += f"🔹 **{code}**: {desc}\n"
        else:
            response += "❌ No data found for this example."

        # Add links (optional)
        response += "\n\n🔗 **Useful Links:**\n"
        response += "[Visit Website](https://example.com) | [Support](https://example.com/support)"

        # Send the response
        await interaction.response.send_message(response, ephemeral=True)

        cursor.close()
        db.close()


# Cog setup
async def setup(bot):
    await bot.add_cog(TemplateCommandPlain(bot))
