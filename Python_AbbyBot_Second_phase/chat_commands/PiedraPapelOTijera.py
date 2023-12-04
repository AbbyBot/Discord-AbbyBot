import discord
from discord.ext import commands
import random
import asyncio

class PiedraPapelOTijera(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ppt(self, ctx, eleccion_usuario: str = None):
        opciones_validas = ['piedra', 'papel', 'tijera']

        if eleccion_usuario is None or eleccion_usuario.lower() not in opciones_validas:
            await ctx.send(f'Por favor, elige entre piedra, papel o tijera.')
            return

        eleccion_usuario = eleccion_usuario.lower()

        await ctx.send(f'{self.bot.user.name} está pensando...')

        await asyncio.sleep(2)  # Espera de 2 segundos (ajusta según sea necesario)

        eleccion_bot = random.choice(opciones_validas)

        resultado = self.obtener_resultado(eleccion_usuario, eleccion_bot)

        await asyncio.sleep(1)  # Espera de 1 segundo antes de mostrar el resultado (ajusta según sea necesario)

        await ctx.send(f'Tú elegiste {eleccion_usuario}. {self.bot.user.name} eligió {eleccion_bot}. {resultado}')

    def obtener_resultado(self, eleccion_usuario, eleccion_bot):
        if eleccion_usuario == eleccion_bot:
            return 'Es un empate.'
        elif (
            (eleccion_usuario == 'piedra' and eleccion_bot == 'tijera') or
            (eleccion_usuario == 'papel' and eleccion_bot == 'piedra') or
            (eleccion_usuario == 'tijera' and eleccion_bot == 'papel')
        ):
            return '¡Ganaste!'
        else:
            return '¡Perdiste!'

def setup(bot):
    bot.add_cog(PiedraPapelOTijera(bot))
