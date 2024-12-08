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


    @app_commands.command(name="dog", description="Show images of random dogs")
    async def dogimg(self, interaction: discord.Interaction):

        # Connect to database with dotenv variables
        db, cursor = get_db_connection()

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

        response = requests.get(url)  # GET request

        if response.status_code == 200:
            data = response.json()
            img_dog = data['url']

        embed = discord.Embed(
            title=f"Here's your dog!" if language_id == 1 else f"Aquí tiene su perro!",
            description="Enjoy your image!" if language_id == 1 else "Disfrute su imagen!",
            color=discord.Color.random()
        )
        embed.set_image(url=img_dog)

        bot_id = 1028065784016142398  # AbbyBot ID
        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

        embed.set_footer(text="Powered by RandomDog API" if language_id == 1 else "Imagen por RandomDog API", icon_url=bot_avatar_url)

        await interaction.followup.send(embed=embed)

        cursor.close()
        db.close()

    @app_commands.command(name="neko", description="Show image of a random nekomimi.")
    async def nekoimg(self, interaction: discord.Interaction):


        # Connect to database with dotenv variables
        db, cursor = get_db_connection()


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
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # Get the language_id of the server
        language_id = result[0]

        url = "https://nekos.best/api/v2/neko"  # API url

        response = requests.get(url)  # GET request

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

            bot_id = 1028065784016142398  # AbbyBot ID
            bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

            embed.set_footer(text="Powered by nekos.best API" if language_id == 1 else "Imagen por nekos.best API", icon_url=bot_avatar_url)

            await interaction.followup.send(embed=embed)
        else:
           # Error handling when the request is not successful
            await interaction.followup.send("Error fetching image.", ephemeral=True)


        cursor.close()
        db.close()

    @app_commands.command(name="waifu", description="Show image of a random waifu, 30 different categories available.")
    @app_commands.choices(categories=[
        discord.app_commands.Choice(name="waifu", value="waifu"),
        discord.app_commands.Choice(name="neko", value="neko"),  
        discord.app_commands.Choice(name="bully", value="bully"),  
        discord.app_commands.Choice(name="cry", value="cry"),    
        discord.app_commands.Choice(name="hug", value="hug"),    
        discord.app_commands.Choice(name="awoo", value="awoo"),
        discord.app_commands.Choice(name="kiss", value="kiss"),
        discord.app_commands.Choice(name="lick", value="lick"),
        discord.app_commands.Choice(name="pat", value="pat"),
        discord.app_commands.Choice(name="smug", value="smug"),
        discord.app_commands.Choice(name="bonk", value="bonk"),
        discord.app_commands.Choice(name="yeet", value="yeet"),
        discord.app_commands.Choice(name="blush", value="blush"),
        discord.app_commands.Choice(name="smile", value="smile"),
        discord.app_commands.Choice(name="wave", value="wave"),
        discord.app_commands.Choice(name="highfive", value="highfive"),
        discord.app_commands.Choice(name="handhold", value="handhold"),
        discord.app_commands.Choice(name="nom", value="nom"),
        discord.app_commands.Choice(name="bite", value="bite"),
        discord.app_commands.Choice(name="glomp", value="glomp"),
        discord.app_commands.Choice(name="happy", value="happy"),
        discord.app_commands.Choice(name="wink", value="wink"),
        discord.app_commands.Choice(name="poke", value="poke"),
        discord.app_commands.Choice(name="dance", value="dance"),
    ])


    async def waifuimg(self, interaction: discord.Interaction, categories: str):
  # Connect to database with dotenv variables
        db, cursor = get_db_connection()

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


        url = f"https://api.waifu.pics/sfw/{categories}" # API url

        response = requests.get(url)  # GET request

        if response.status_code == 200:
            data = response.json()
            img_waifu = data['url']

        embed = discord.Embed(
            title=f"Here's your {categories} image!" if language_id == 1 else f"Aquí tiene su imagen de categoría {categories}!",
            description="Enjoy your image!" if language_id == 1 else "Disfrute su imagen!",
            color=discord.Color.random()
        )
        embed.set_image(url=img_waifu)


        bot_id = 1028065784016142398  # AbbyBot ID
        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)
    
        embed.set_footer(text="Powered by waifu.pics API" if language_id == 1 else "Imagen por waifu.pics API", icon_url=bot_avatar_url)

        await interaction.response.send_message(embed=embed)

        cursor.close()
        db.close()


