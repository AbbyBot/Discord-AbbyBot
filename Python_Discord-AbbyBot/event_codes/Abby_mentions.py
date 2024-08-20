import discord
from discord.ext import commands
import sqlite3

# Base de datos
conn = sqlite3.connect('abby_database.db')
cursor = conn.cursor()

class Abby_mentions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.mention_count = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return


        if self.bot.user.mentioned_in(message):
            author_username = str(message.author.name)
            author_id = str(message.author.id)
            if author_id not in self.bot.mention_count:
                self.bot.mention_count[author_id] = 1
            else:
                self.bot.mention_count[author_id] += 1
                print(f'DEBUG: User: {author_username} \n ID: {author_id} \n Tags: {self.bot.mention_count[author_id]}')

                if self.bot.mention_count[author_id] > 7:
                    cursor.execute("SELECT contenido FROM forgiveness_responses ORDER BY RANDOM() LIMIT 1")
                    forgiveness_result = cursor.fetchone()
                    mensaje = forgiveness_result[0] if forgiveness_result else "I forgive you this time."
                    await message.channel.send(mensaje)

                    self.bot.mention_count[author_id] = 0
                    print(f'DEBUG: Counter reset for: \n User: {author_username} \n ID: {author_id} \n Tags: {self.bot.mention_count[author_id]}')

                    return
                elif self.bot.mention_count[author_id] > 3:
                    cursor.execute("SELECT contenido FROM angry_responses ORDER BY RANDOM() LIMIT 1")
                    resultado = cursor.fetchone()
                    mensaje = resultado[0] if resultado else "You're bothering me too much!"
                    await message.channel.send(mensaje)
                    return

            cursor.execute("SELECT contenido FROM tag_responses ORDER BY RANDOM() LIMIT 1")
            resultado = cursor.fetchone()
            mensaje = resultado[0] if resultado else "Right now I don't know how to answer you :/"
            await message.channel.send(mensaje)

def setup(bot):
    bot.add_cog(Abby_mentions(bot))
