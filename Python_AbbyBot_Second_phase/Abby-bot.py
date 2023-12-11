# Importación de librerías

import discord
from discord.ext import commands


# Imporatcion de comandos

from chat_commands.saludos import Saludos
from chat_commands.PiedraPapelOTijera import PiedraPapelOTijera
from chat_commands.ping import Ping
from chat_commands.Codear import Codear
from chat_commands.Ayuda import Ayuda
from chat_commands.Obtener_acceso import ObtenerAcceso


# Importacion de eventos

from event_codes.Deleted_messages import Deleted_Messages
from event_codes.Abby_mentions import Abby_mentions
from event_codes.Banned_URLs_Warn import Banned_URLs




# Prefijo del bot

bot = commands.Bot(command_prefix='abby_', intents=discord.Intents.all())

@bot.event # Cargar todos los archivos de comandos extras
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    await bot.add_cog(Saludos(bot))
    await bot.add_cog(Ping(bot))
    await bot.add_cog(PiedraPapelOTijera(bot))
    await bot.add_cog(Codear(bot))
    await bot.add_cog(ObtenerAcceso(bot))
    await bot.add_cog(Deleted_Messages(bot))
    await bot.add_cog(Abby_mentions(bot))
    await bot.add_cog(Ayuda(bot))
    await bot.add_cog(Banned_URLs(bot))


    
bot.run(' >:( ') # Token, Siempre cambiar antes de hacer un commit mensito



