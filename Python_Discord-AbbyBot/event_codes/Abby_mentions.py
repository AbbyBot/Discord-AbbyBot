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
            author_id = str(message.author.id)
            if author_id not in self.bot.mention_count:
                self.bot.mention_count[author_id] = 1
            else:
                self.bot.mention_count[author_id] += 1
                print(f'Menciones para {author_id}: {self.bot.mention_count[author_id]}')

                if self.bot.mention_count[author_id] > 7:
                    cursor.execute("SELECT contenido FROM forgiveness_responses ORDER BY RANDOM() LIMIT 1")
                    forgiveness_result = cursor.fetchone()
                    mensaje = forgiveness_result[0] if forgiveness_result else 'Te perdono esta vez.'
                    await message.channel.send(mensaje)

                    self.bot.mention_count[author_id] = 0
                    print(f'Contador reiniciado para {author_id}')
                    return
                elif self.bot.mention_count[author_id] > 3:
                    cursor.execute("SELECT contenido FROM angry_responses ORDER BY RANDOM() LIMIT 1")
                    resultado = cursor.fetchone()
                    mensaje = resultado[0] if resultado else '¡Me estás molestando demasiado!'
                    await message.channel.send(mensaje)
                    return

            cursor.execute("SELECT contenido FROM tag_responses ORDER BY RANDOM() LIMIT 1")
            resultado = cursor.fetchone()
            mensaje = resultado[0] if resultado else 'En estos momentos no sé cómo responderte :/ '
            await message.channel.send(mensaje)

def setup(bot):
    bot.add_cog(Abby_mentions(bot))
