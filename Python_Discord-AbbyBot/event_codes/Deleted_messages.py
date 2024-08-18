import discord
from discord.ext import commands
import random
import sqlite3

# Base de datos
conn = sqlite3.connect('abby_database.db')
cursor = conn.cursor()

class Deleted_Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        message_probability = random.randint(1, 5)
        print(f"Valor message_probability: {message_probability}")

        if message_probability == 1:

            cursor.execute("SELECT contenido FROM delete_responses ORDER BY RANDOM() LIMIT 1")
            forgiveness_result = cursor.fetchone()
            mensaje = forgiveness_result[0]

            await message.channel.send(mensaje)

def setup(bot):
    bot.add_cog(Deleted_Messages(bot))
