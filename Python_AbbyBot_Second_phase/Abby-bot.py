import discord
from discord.ext import commands
from chat_commands.saludos import Saludos
from chat_commands.PiedraPapelOTijera import PiedraPapelOTijera
from chat_commands.ping import Ping
from chat_commands.Codear import Codear
import sqlite3
import pyjokes
import random

conn = sqlite3.connect('abby_database.db')
cursor = conn.cursor()


bot = commands.Bot(command_prefix='abby_', intents=discord.Intents.all())

@bot.event # Cargará todos los archivos de comandos extras
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    await bot.add_cog(Saludos(bot))
    await bot.add_cog(Ping(bot))
    await bot.add_cog(PiedraPapelOTijera(bot))
    await bot.add_cog(Codear(bot))

@bot.event # Si alguien usa el "abby_" pero no escribe nada más
async def on_message(message):
    # Verifica si el mensaje comienza con el prefijo del bot y si el autor no es el propio bot
    if message.content.startswith(bot.command_prefix) and message.author != bot.user:
        # Verifica si el mensaje no es un comando válido
        if not bot.get_command(message.content[len(bot.command_prefix):]):
            # Responde con un mensaje personalizado
            await message.channel.send("Por favor, escriba un comando válido.")
            await message.channel.send("Puedes usar 'abby_ayuda' ")

    # Permite que otros comandos y eventos sigan ejecutándose
    await bot.process_commands(message)

bot.mention_count = {}  # Inicializar el diccionario de menciones

@bot.event # Sistema de menciones
async def on_message(message):
    if message.author == bot.user:
        return

    # Verificar si el bot fue mencionado en el mensaje
    if bot.user.mentioned_in(message):
        # Lógica para el bot enojado
        author_id = str(message.author.id)
        if author_id not in bot.mention_count:
            bot.mention_count[author_id] = 1
        else:
            bot.mention_count[author_id] += 1
            print(f'Menciones para {author_id}: {bot.mention_count[author_id]}')

            if bot.mention_count[author_id] > 7:  # Umbral para mensaje de perdón
                cursor.execute("SELECT contenido FROM forgiveness_responses ORDER BY RANDOM() LIMIT 1")
                forgiveness_result = cursor.fetchone()
                if forgiveness_result:
                    mensaje = forgiveness_result[0]
                else:
                    mensaje = 'Te perdono esta vez.'
                await message.channel.send(mensaje)

                # Restablecer el contador a 0
                bot.mention_count[author_id] = 0
                print(f'Contador reiniciado para {author_id}')
                return  # No enviar el mensaje normal si se envió un mensaje de perdón
            elif bot.mention_count[author_id] > 3:  # Umbral para enojo
                cursor.execute("SELECT contenido FROM angry_responses ORDER BY RANDOM() LIMIT 1")
                resultado = cursor.fetchone()
                if resultado:
                    mensaje = resultado[0]
                else:
                    mensaje = '¡Me estás molestando demasiado!'
                await message.channel.send(mensaje)
                return  # No enviar el mensaje normal si se envió un mensaje de enojo

        # Mensaje normal
        cursor.execute("SELECT contenido FROM tag_responses ORDER BY RANDOM() LIMIT 1")
        resultado = cursor.fetchone()
        if resultado:
            mensaje = resultado[0]
        else:
            mensaje = 'En estos momentos no sé cómo responderte :/ '
        await message.channel.send(mensaje)
    else:
        # Verifica si el mensaje comienza con el prefijo del bot y si el autor no es el propio bot
        if message.content.startswith(bot.command_prefix) and message.author != bot.user:
            # Verifica si el mensaje no es un comando válido
            if not bot.get_command(message.content[len(bot.command_prefix):]):
                # Responde con un mensaje personalizado
                await message.channel.send("Por favor, escriba un comando válido.")

    # Permite que otros comandos y eventos sigan ejecutándose
    await bot.process_commands(message)

@bot.command()
async def chiste(ctx):
    joke = pyjokes.get_joke(language='es', category='all')
    await ctx.send(joke)




@bot.event
async def on_message_delete(message):

    message_probability = random.randint(1,5)
    print(f"Valor message_probability: {message_probability}")

    if message_probability == 1:

        cursor.execute("SELECT contenido FROM delete_responses ORDER BY RANDOM() LIMIT 1")
        forgiveness_result = cursor.fetchone()
        mensaje = forgiveness_result[0]

        await message.channel.send(mensaje)
    pass

@bot.event
async def on_message_edit(before, after):
    #Coming soon
    pass



    
bot.run(' >:( ')


