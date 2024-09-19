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

class WaifuImg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="waifu_img", description="Show image of a random waifu, 30 different categories available.")
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

        response = requests.get(url)  # GET petition

        if response.status_code == 200:
            data = response.json()
            img_waifu = data['url']

        embed = discord.Embed(
            title=f"Here's your {categories} image!" if language_id == 1 else f"Aquí tiene su imagen de categoría {categories}!",
            description="Enjoy your image!" if language_id == 1 else "Disfrute su imagen!",
            color=discord.Color.random()
        )
        embed.set_image(url=img_waifu)
        embed.set_footer(text="Powered by waifu.pics API" if language_id == 1 else "Imagen por waifu.pics API")

        await interaction.response.send_message(embed=embed)

        cursor.close()
        db.close()
