import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os
import requests
from embeds.embeds import account_inactive_embed

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

        # If the user is inactive (is_active = 0), send an embed in DM and exit
        is_active = result[0]
        if is_active == 0:
            try:
                # Send the embed message as a DM
                await interaction.user.send(embed=account_inactive_embed())
                print(f"User {interaction.user} is inactive and notified.")
            except discord.Forbidden:
                print(f"Could not send DM to {interaction.user}. They may have DMs disabled.")

            await interaction.response.send_message("Request Rejected: Your account has been listed as **inactive** in the AbbyBot system, please check your DM.", ephemeral=True)

            cursor.close()
            db.close()
            return
        else: # user are not "banned"
            await interaction.response.defer()

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
            embed.add_field(name="Source" if language_id == 1 else "Recurso", value=f"[{'Go URL' if language_id == 1 else 'Ir a la URL'}]({source_url})", inline=False)
            
            embed.set_image(url=img_neko)
            embed.set_footer(text="Powered by nekos.best API" if language_id == 1 else "Imagen por nekos.best API")

            await interaction.followup.send(embed=embed)
        else:
           # Error handling when the request is not successful
            await interaction.followup.send("Error fetching image.", ephemeral=True)


        cursor.close()
        db.close()
