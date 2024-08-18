import discord
from discord import app_commands
from discord.ext import commands

class Code(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="code", description="Send code formatted for convenience.")
    async def codear(self, interaction: discord.Interaction, code: str):
        await interaction.response.defer()  # Delete the message temporarily while processing
        await interaction.followup.send(f"```\n{code}\n```")