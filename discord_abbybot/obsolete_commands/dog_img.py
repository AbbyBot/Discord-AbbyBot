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

class DogImg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dog_img", description="Show images of random dogs")
    async def dogimg(self, interaction: discord.Interaction):

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
        cursor.execute("SELECT is_active FROM user_profile WHERE user_id = %s;", (user_id,))
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
                # Get the embed and file
                embed, file = account_inactive_embed()

                # Send the embed and the file as DM
                await interaction.user.send(embed=embed, file=file)
                
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
            await interaction.followup.send("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # Get the language_id of the server
        language_id = result[0]

        url = f"https://random.dog/woof.json" # API url

        response = requests.get(url)  # GET petition

        if response.status_code == 200:
            data = response.json()
            img_dog = data['url']

        embed = discord.Embed(
            title=f"Here's your dog!" if language_id == 1 else f"Aquí tiene su perro!",
            description="Enjoy your image!" if language_id == 1 else "Disfrute su imagen!",
            color=discord.Color.random()
        )
        embed.set_image(url=img_dog)
        embed.set_footer(text="Powered by RandomDog API" if language_id == 1 else "Imagen por RandomDog API")

        await interaction.followup.send(embed=embed)

        cursor.close()
        db.close()
