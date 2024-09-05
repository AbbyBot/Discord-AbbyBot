import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os
import requests


# Load dotenv variables
load_dotenv()

class NekoImg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="neko_img", description="Show image of a random nekomimi.")
    async def waifuimg(self, interaction: discord.Interaction):



  # Connect to database with dotenv variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Check if server is registered
        guild_id = interaction.guild_id
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            # if server is not registered, send error message
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # Get the language_id of the server
        language_id = result[0]

        url = "https://nekos.best/api/v2/neko"  # API url

        response = requests.get(url)  # GET petition

        if response.status_code == 200:
            data = response.json()

            # Get 'results' data
            result = data['results'][0]
            
            artist_href = result.get('artist_href', 'No artist link available')
            artist_name = result.get('artist_name', 'Unknown artist')
            source_url = result.get('source_url', 'No source available')
            img_neko = result.get('url', '')


            embed = discord.Embed(
                title=f"Here's your image!" if language_id == 1 else f"Aquí tiene su imagen!",
                description="Enjoy your image!" if language_id == 1 else "Disfrute su imagen!",
                color=discord.Color.random()
            )

            embed.add_field(name="Artist" if language_id == 1 else "Artista", value=f"[{artist_name}]({artist_href})", inline=False)
            embed.add_field(name="Source" if language_id == 1 else "Recurso", value=f"[{artist_name}]({source_url})", inline=False)
            
            embed.set_image(url=img_neko)
            embed.set_footer(text="Powered by nekos.best API" if language_id == 1 else "Imagen por nekos.best API")

            await interaction.response.send_message(embed=embed)
        else:
           # Error handling when the request is not successful
            await interaction.response.send_message("Error fetching image.", ephemeral=True)




