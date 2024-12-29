from discord.ext import commands
from discord import app_commands
import discord

class FortniteCommands(commands.GroupCog, name="fortnite"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Show Fortnite profile information.")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello World", ephemeral=True)

    @app_commands.command(name="map", description="Show the current Fortnite map.")
    async def map(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello World", ephemeral=True)

    @app_commands.command(name="store", description="Show the current Fortnite store.")
    async def store(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello World", ephemeral=True)
