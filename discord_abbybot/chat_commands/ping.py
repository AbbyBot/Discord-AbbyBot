import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
from utils.db_utils import get_db_connection


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check your latency with the server.")
    async def ping(self, interaction: discord.Interaction):

        db, cursor = get_db_connection()

        # Get guild_id and user_id from the interaction
        guild_id = interaction.guild_id
        user_id = interaction.user.id

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
            await interaction.response.send_message("Pinging...") 

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

            await interaction.channel.send(content=f'🏓 Pong!\n**Bot latency:** {bot_latency} ms\n**Your estimated ping:** {final_ping} ms\n{criticism}')
       
        elif language_id == 2:
            await interaction.response.send_message("Haciendo ping...") 

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

            await interaction.channel.send(content=f'🏓 ¡Pong!\n**Latencia del bot:** {bot_latency} ms\n**Tu ping estimado:** {final_ping} ms\n{criticism}')
        
        # Close db connection
        cursor.close()
        db.close()