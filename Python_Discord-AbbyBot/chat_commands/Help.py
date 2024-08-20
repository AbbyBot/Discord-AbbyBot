import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Do you have any questions?")
    async def help(self, interaction: discord.Interaction):
        # Create embed
        embed = discord.Embed(
            title="Help",
            description="At the moment this section is as work in process (W.I.P), we apologize for the inconvenience.",
            color=discord.Color.from_rgb(145, 61, 33)  # Change colors
        )

        # Add more fields
        embed.add_field(name="Command 1", value="Command 2 Description", inline=False)
        embed.add_field(name="Command 2", value="Command 2 Description", inline=False)

        # Abbybot's pfp.png file
        image_path = "abbybot.png"

        # Load image like Discord file
        file = discord.File(image_path, filename="abbybot.png")

        # Add img to embed
        embed.set_image(url="attachment://abbybot.png")

        # Send message
        await interaction.response.send_message(embed=embed, file=file)

async def setup(bot):
    await bot.add_cog(Help(bot))
