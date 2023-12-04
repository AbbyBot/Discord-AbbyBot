import discord
from discord.ext import commands
from chat_commands.saludos import Saludos
from chat_commands.PiedraPapelOTijera import PiedraPapelOTijera
from chat_commands.ping import Ping

bot = commands.Bot(command_prefix='abby_', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    await bot.add_cog(Saludos(bot))
    await bot.add_cog(Ping(bot))
    await bot.add_cog(PiedraPapelOTijera(bot))
# Registra los comandos desde los archivos importados

# Coloca aquí el resto de tu código, como el token y la ejecución del bot

bot.run('SECRETO')



