from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import discord
import requests
import os



class FortniteCommands(commands.GroupCog, name="fortnite"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Show Fortnite profile information.")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello World", ephemeral=True)

    @app_commands.command(name="map", description="Show the current Fortnite map.")
    @app_commands.describe(option="Choose between 'blank' or 'with names'")
    @app_commands.choices(option=[
        app_commands.Choice(name="Blank", value="blank"),
        app_commands.Choice(name="With Names", value="with_names")
    ])
    async def map(self, interaction: discord.Interaction, option: str):

        await interaction.response.defer()
        
        response = requests.get("https://fortnite-api.com/v1/map")
        if response.status_code == 200:
            data = response.json()
            images = data['data']['images']
            if option == "blank":
                image_url = images['blank']
            else:
                image_url = images['pois']
            
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                with open("/tmp/fortnite_map.png", "wb") as file:
                    file.write(image_response.content)
                
                file = discord.File("/tmp/fortnite_map.png", filename="fortnite_map.png")
                embed = discord.Embed(
                    title="Fortnite Map",
                    description="Here is the latest Fortnite map. Choose your landing spot wisely!",
                    color=discord.Color.random()
                )
                
                footer_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "abbybot.png")
                footer_file = discord.File(footer_image_path, filename="abbybot.png")
                embed.set_image(url="attachment://fortnite_map.png")
                embed.set_footer(text=f"AbbyBot • Map fetched on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC", icon_url="attachment://abbybot.png")
                
                await interaction.followup.send(embed=embed, files=[file, footer_file], ephemeral=False)
            else:
                await interaction.followup.send("Sorry, we couldn't download the map image at this time. Please try again later.", ephemeral=True)
        else:
            await interaction.followup.send("Sorry, we couldn't retrieve the map data at this time. Please try again later.", ephemeral=True)

    @app_commands.command(name="store", description="Show the current Fortnite store.")
    async def store(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello World", ephemeral=True)
