import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import mysql.connector
from dotenv import load_dotenv
import os
import random
from embeds.embeds import account_inactive_embed

# Load dotenv variables
load_dotenv()

# load all .env Emojis
emojis_str = os.getenv("EMOJIS", "")  # Get the string, default will be an empty string if not defined

# Check if global variable have content
if not emojis_str:
    emojis = [" "]  # Use blank space if variable doesn't have content
else:
    emojis = emojis_str.split(',')  # Separate string in a list of emojis

# Choose a random emoji (or space if there are no emojis)
random_emoji = random.choice(emojis)


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check your latency with the server.")
    async def ping(self, interaction: discord.Interaction):

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
        
        # Query to check the server's language setting (obligatory field)
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return
        
        # Get server language
        
        language_id = result[0]  # Get language ID

        # Validate the language

        if language_id == 1:

            await interaction.response.send_message(f"Pinging... {random_emoji} ") 

            # Calculate bot latency
            bot_latency = round(self.bot.latency * 1000)

            # Simulates a possible variation in the ping
            ping_variation = random.randint(-20, 20)
            final_ping = bot_latency + ping_variation

            if final_ping < 50:
                criticism = "Awesome! Your internet is faster than lightning."
            elif 50 <= final_ping < 100:
                criticism = "Your connection is decent, but you could do better."
            elif 100 <= final_ping < 200:
                criticism = "Are we in the dial-up era? A little slow, right?"
            else:
                criticism = "Houston, we have a problem! Your internet is in the age of the dinosaurs."

            await asyncio.sleep(2) 

            await interaction.channel.send(content=f'Pong! 🏓\nBot latency: {bot_latency} ms\nYour estimated ping: {final_ping} ms\n{criticism}')
       
        elif language_id == 2:

            await interaction.response.send_message(f"Haciendo ping... {random_emoji}") 

            # Calculate bot latency
            bot_latency = round(self.bot.latency * 1000)

            # Simulates a possible variation in the ping
            ping_variation = random.randint(-20, 20)
            final_ping = bot_latency + ping_variation

            if final_ping < 50:
                criticism = "¡Impresionante! Tu Internet es más rápido que un rayo."
            elif 50 <= final_ping < 100:
                criticism = "Tu conexión es decente, pero podrías hacerlo mejor."
            elif 100 <= final_ping < 200:
                criticism = "¿Estamos en la era del acceso telefónico? Un poco lento ¿no?"
            else:
                criticism = "¡Houston, tenemos un problema! Tu Internet está en la era de los dinosaurios."

            await asyncio.sleep(2) 

            await interaction.channel.send(content=f'Pong! 🏓\nLatencia del bot: {bot_latency} ms\nTu ping estimado: {final_ping} ms\n{criticism}')
        
        # Close db connection
        cursor.close()
        db.close()