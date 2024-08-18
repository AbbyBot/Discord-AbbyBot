import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Do you have any questions?")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message("DEBUG: This is a test message.") 

