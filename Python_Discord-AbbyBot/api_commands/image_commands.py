import discord
from discord.ext import commands
from discord import app_commands
import requests
import random
import string
from embeds.embeds import account_inactive_embed
from utils.utils import get_bot_avatar
from utils.db_utils import get_db_connection
import os

class ImageCommands(commands.GroupCog, name="image"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cat", description="Show images of random cats 😼")
    @app_commands.choices(categories=[
        discord.app_commands.Choice(name="cat", value=1),
        discord.app_commands.Choice(name="gif", value=2),  
        discord.app_commands.Choice(name="with text", value=3),  
    ])
    async def catimg(self, interaction: discord.Interaction, categories: int, text: str = None):
        await interaction.response.defer()  # Always defer 
        
        db, cursor = get_db_connection()

        try:
            # Get the server's language setting
            guild_id = interaction.guild_id
            cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if result is None:
                await interaction.followup.send("This server is not registered. Please contact the admin.", ephemeral=True)
                return

            language_id = result[0]

            # Validate input for category 3
            if categories == 3 and text is None:
                msg = "Please provide the text for the image." if language_id == 1 else "Por favor proporcione el texto de la imagen."
                await interaction.followup.send(msg, ephemeral=True)
                return

            # Determine URL and file extension
            if categories == 1:
                url = "https://cataas.com/cat"
                file_extension = 'png'
            elif categories == 2:
                url = "https://cataas.com/cat/gif"
                file_extension = 'gif'
            elif categories == 3:
                url = f"https://cataas.com/cat/says/{text}?fontSize=50&fontColor=white"
                file_extension = 'png'

            # Download the image
            response = requests.get(url)
            if response.status_code != 200:
                await interaction.followup.send("Failed to retrieve cat image. Please try again later.", ephemeral=True)
                return

            # Save the image to a temporary file
            filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + f'.{file_extension}'
            img_path = f'/tmp/{filename}'
            with open(img_path, 'wb') as f:
                f.write(response.content)

            file = discord.File(img_path, filename=filename)

            # Create embed
            embed = discord.Embed(
                title="Here's your cat image!" if language_id == 1 else "Aquí tiene su imagen de gato!",
                color=discord.Color.random()
            )
            embed.add_field(
                name="🔗 Image Credit",
                value="Powered by [cataas.com](https://cataas.com)" if language_id == 1 else "Proporcionada por [cataas.com](https://cataas.com)",
                inline=False
            )
            embed.set_image(url=f"attachment://{filename}")

            # Set thumbnail
            thumbnail_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "profile_emotes", "abbybot_heart.png")
            thumbnail_file = discord.File(thumbnail_path, filename="abbybot_thumbnail.png")
            embed.set_thumbnail(url="attachment://abbybot_thumbnail.png")

            footer_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "abbybot.png")
            footer_file = discord.File(footer_image_path, filename="abbybot.png")
            embed.set_footer(text="AbbyBot • Your Discord Ally", icon_url="attachment://abbybot.png")

            # Create button
            view = discord.ui.View()
            button = discord.ui.Button(label="Visit AbbyBot Website", url="https://abbybotproject.com")
            view.add_item(button)

            # Send response
            await interaction.followup.send(embed=embed, files=[file, thumbnail_file, footer_file], view=view)

        except Exception as e:
            print(f"Error in 'catimg' command: {e}")
            await interaction.followup.send("An unexpected error occurred. Please try again later.", ephemeral=True)

        finally:
            cursor.close()
            db.close()


    @app_commands.command(name="dog", description="Show images of random dogs 🐶")
    async def dogimg(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Always defer

        db, cursor = get_db_connection()

        try:
            # Get the server's language setting
            guild_id = interaction.guild_id
            cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if result is None:
                await interaction.followup.send("This server is not registered. Please contact the admin.", ephemeral=True)
                return

            language_id = result[0]

            # Fetch a random dog image from the API
            url = "https://random.dog/woof.json"  # Random Dog API URL
            response = requests.get(url)

            if response.status_code != 200:
                await interaction.followup.send("Failed to retrieve dog image. Please try again later.", ephemeral=True)
                return

            data = response.json()
            img_dog = data["url"]

            # Create embed
            embed = discord.Embed(
                title="Here's your dog image!" if language_id == 1 else "Aquí tiene su imagen de perro!",
                color=discord.Color.random()
            )
            embed.add_field(
                name="🔗 Image Credit",
                value="Powered by [random.dog](https://random.dog)" if language_id == 1 else "Proporcionada por [random.dog](https://random.dog)",
                inline=False
            )
            embed.set_image(url=img_dog)

            # Add thumbnail and footer
            thumbnail_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "profile_emotes", "abbybot_heart.png")
            thumbnail_file = discord.File(thumbnail_path, filename="abbybot_thumbnail.png")
            embed.set_thumbnail(url="attachment://abbybot_thumbnail.png")

            footer_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "abbybot.png")
            footer_file = discord.File(footer_image_path, filename="abbybot.png")
            embed.set_footer(text="AbbyBot • Your Discord Ally", icon_url="attachment://abbybot.png")

            # Add button
            view = discord.ui.View()
            button = discord.ui.Button(label="Visit AbbyBot Website", url="https://abbybotproject.com")
            view.add_item(button)

            # Send response to the user
            await interaction.followup.send(embed=embed, files=[thumbnail_file, footer_file], view=view)

        except Exception as e:
            print(f"Error in 'dogimg' command: {e}")
            await interaction.followup.send("An unexpected error occurred. Please try again later.", ephemeral=True)

        finally:
            cursor.close()
            db.close()


    @app_commands.command(name="neko", description="Show image of a random nekomimi.")
    async def nekoimg(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Always defer
        db, cursor = get_db_connection()

        try:
            # Get the server's language setting
            guild_id = interaction.guild_id
            cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if result is None:
                await interaction.followup.send("This server is not registered. Please contact the admin.", ephemeral=True)
                return

            language_id = result[0]

            # Fetch random neko image from the API
            url = "https://nekos.best/api/v2/neko"  # Nekos.best API URL
            response = requests.get(url)

            if response.status_code != 200:
                await interaction.followup.send("Failed to retrieve nekomimi image. Please try again later.", ephemeral=True)
                return

            data = response.json()
            result = data['results'][0]

            # Extract information from the API response
            artist_href = result.get('artist_href', 'No artist link available')
            artist_name = result.get('artist_name', 'Unknown artist')
            source_url = result.get('source_url', 'No source available')
            img_neko = result.get('url', '')

            # Create embed
            embed = discord.Embed(
                title="Here's your nekomimi image!" if language_id == 1 else "Aquí tiene su imagen de nekomimi!",
                color=discord.Color.random()
            )
            embed.add_field(
                name="🎨 Artist" if language_id == 1 else "🎨 Artista",
                value=f"[{artist_name}]({artist_href})",
                inline=False
            )
            embed.add_field(
                name="🔗 Source" if language_id == 1 else "🔗 Recurso",
                value=f"[{'Go URL' if language_id == 1 else 'Ir a la URL'}]({source_url})",
                inline=False
            )
            embed.set_image(url=img_neko)

            # Add thumbnail and footer
            thumbnail_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "profile_emotes", "abbybot_heart.png")
            thumbnail_file = discord.File(thumbnail_path, filename="abbybot_thumbnail.png")
            embed.set_thumbnail(url="attachment://abbybot_thumbnail.png")

            footer_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "abbybot.png")
            footer_file = discord.File(footer_image_path, filename="abbybot.png")
            embed.set_footer(text="AbbyBot • Your Discord Ally", icon_url="attachment://abbybot.png")

            # Add button
            view = discord.ui.View()
            button = discord.ui.Button(label="Visit AbbyBot Website", url="https://abbybotproject.com")
            view.add_item(button)

            # Send response to the user
            await interaction.followup.send(embed=embed, files=[thumbnail_file, footer_file], view=view)

        except Exception as e:
            print(f"Error in 'nekoimg' command: {e}")
            await interaction.followup.send("An unexpected error occurred. Please try again later.", ephemeral=True)

        finally:
            cursor.close()
            db.close()

    @app_commands.command(name="waifu",description="Show a random waifu image from a random category.")
    async def random_waifu(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Always defer the response

        WAIFU_CATEGORIES = [
            "waifu", "neko", "shinobu", "megumin", "bully", "cuddle", "cry", "hug", "awoo", 
            "kiss", "lick", "pat", "smug", "blush", "smile", "wave", "poke", "dance", 
            "happy", "wink", "nom", "bite", "slap", "kick", "cringe", "bonk", "yeet", 
            "handhold", "glomp", "kill"
        ]

        try:
            # Select a random category
            category = random.choice(WAIFU_CATEGORIES)

            # Fetch waifu image from the API
            url = f"https://api.waifu.pics/sfw/{category}"  # API URL
            response = requests.get(url)

            if response.status_code != 200:
                await interaction.followup.send("Failed to retrieve waifu image. Please try again later.", ephemeral=True)
                return

            data = response.json()
            img_waifu = data["url"]

            # Create embed
            embed = discord.Embed(
                title=f"Here's a random {category} image!",
                color=discord.Color.random()
            )
            embed.add_field(
                name="🔗 Image Credit",
                value="Powered by [waifu.pics](https://waifu.pics)",
                inline=False
            )
            embed.set_image(url=img_waifu)

            # Add thumbnail
            thumbnail_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "profile_emotes", "abbybot_heart.png")
            thumbnail_file = discord.File(thumbnail_path, filename="abbybot_thumbnail.png")
            embed.set_thumbnail(url="attachment://abbybot_thumbnail.png")

            # Add footer
            footer_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "abbybot.png")
            footer_file = discord.File(footer_image_path, filename="abbybot.png")
            embed.set_footer(
                text="AbbyBot • Your Discord Ally",
                icon_url="attachment://abbybot.png"
            )

            # Create button
            view = discord.ui.View()
            button = discord.ui.Button(label="Visit AbbyBot Website", url="https://abbybotproject.com")
            view.add_item(button)

            # Send response
            await interaction.followup.send(embed=embed, files=[thumbnail_file, footer_file], view=view)

        except Exception as e:
            print(f"Error in 'random_waifu' command: {e}")
            await interaction.followup.send("An unexpected error occurred. Please try again later.", ephemeral=True)
