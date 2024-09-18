import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class Code(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="code", description="Send code formatted for convenience.")
    async def command_name(self, interaction: discord.Interaction, code: str):
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
        cursor.execute("SELECT is_active FROM dashboard WHERE guild_id = %s AND user_id = %s", (guild_id, user_id))
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
                # Create the embed message
                embed = discord.Embed(
                    title="Account Inactive Notice",
                    description=(
                        "Your account has been marked as **inactive** because you likely chose not to participate in the AbbyBot project.\n\n"
                        "As a result, you will no longer be able to send commands or trigger events while this status remains.\n\n"
                        "If you believe this was an error, please send a message to [Support URL](https://url1.com).\n"
                        "Otherwise, if you opted out voluntarily but have changed your mind, you can fill out a form at [Reactivation Form](https://url2.com) "
                        "where an admin will review your request to reinstate your account."
                    ),
                    color=discord.Color.red()
                )
                embed.set_footer(text="Thank you for your understanding.")
                
                # Send the embed message as a DM
                await interaction.user.send(embed=embed)
                print(f"User {interaction.user} is inactive and notified.")
            except discord.Forbidden:
                print(f"Could not send DM to {interaction.user}. They may have DMs disabled.")
            
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

        # Send the response
        await interaction.response.defer()  # Delete the message temporarily while processing
        await interaction.followup.send(f"```\n{code}\n```")

        # Close the database connection
        cursor.close()
        db.close()

# Add cog command
async def setup(bot):
    await bot.add_cog(Code(bot))
