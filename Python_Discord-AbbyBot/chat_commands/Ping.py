import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="check your latency in ms with the server.")
    async def base(self, interaction: discord.Interaction):

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

        await interaction.channel.send(content=f'Pong! 🏓\nBot latency: {bot_latency} ms\nYour estimated ping: {final_ping} ms\n{criticism}')





