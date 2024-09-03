import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os
import requests
import random
import string


# Load dotenv variables
load_dotenv()

class CatImg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cat_img", description="Show images of random cats 😼")
    @app_commands.choices(categories=[
        discord.app_commands.Choice(name="cat", value=1),
        discord.app_commands.Choice(name="gif", value=2),  
        discord.app_commands.Choice(name="with text", value=3),  
    ])
    async def catimg(self, interaction: discord.Interaction, categories: int, text: str = None):

        # Defer the response to avoid the interaction timeout
        await interaction.response.defer()

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
            await interaction.followup.send("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # Get the language_id of the server
        language_id = result[0]

        if categories == 3 and text is None:
            if language_id == 1:
                await interaction.followup.send("Please provide the text for the image.")
                return
            if language_id == 2:
                await interaction.followup.send("Por favor proporcione el texto de la imagen.")
                return

        if categories == 1:
            url = "https://cataas.com/cat"
            file_extension = 'png'
        elif categories == 2:
            url = "https://cataas.com/cat/gif"
            file_extension = 'gif'
        elif categories == 3:
            url = f"https://cataas.com/cat/says/{text}?fontSize=50&fontColor=white"
            file_extension = 'png'

        # Perform the GET request
        response = requests.get(url)

        if response.status_code == 200:
            # Generate a random filename
            filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + f'.{file_extension}'
            img_path = f'/tmp/{filename}'

            # Save the image content directly to a file
            with open(img_path, 'wb') as f:
                f.write(response.content)

            file = discord.File(img_path, filename=filename)

            embed = discord.Embed(
                title="Here's your cat image!" if language_id == 1 else "Aquí tiene su imagen de gato!",
                description="Enjoy your image!" if language_id == 1 else "Disfrute su imagen!",
                color=discord.Color.random()
            )
            embed.set_image(url=f"attachment://{filename}")
            embed.set_footer(text="Powered by cataas.com" if language_id == 1 else "Imagen por cataas.com")

            # Send the final response with the image
            await interaction.followup.send(embed=embed, file=file)

        else:
            await interaction.followup.send("Failed to retrieve cat image. Please try again later.", ephemeral=True)

        cursor.close()
        db.close()
