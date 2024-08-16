import discord
from discord import app_commands
from discord.ext import commands

class Codear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="codear", description="Envía código formateado")
    async def codear(self, interaction: discord.Interaction, codigo: str):
        await interaction.response.defer()  # Esto elimina el mensaje temporalmente mientras procesa
        await interaction.followup.send(f"```\n{codigo}\n```")

async def setup(bot):
    await bot.add_cog(Codear(bot))
