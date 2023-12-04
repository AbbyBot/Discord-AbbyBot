import discord
from discord.ext import commands
import asyncio
import random

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        mensaje_ping = await ctx.send("Pinging...")

        # Calcula la latencia del bot
        bot_latencia = round(self.bot.latency * 1000)

        # Simula una posible variación en el ping
        variacion_ping = random.randint(-20, 20)
        ping_final = bot_latencia + variacion_ping

        if ping_final < 50:
            critica = "¡Impresionante! Tu internet es más rápido que un rayo."
        elif 50 <= ping_final < 100:
            critica = "Tu conexión es decente, pero podrías hacerlo mejor."
        elif 100 <= ping_final < 200:
            critica = "¿Estamos en la era de dial-up? Un poco lento, ¿no?"
        else:
            critica = "¡Houston, tenemos un problema! Tu internet está en la era de los dinosaurios."

        await asyncio.sleep(2)  # Simula una pequeña espera antes de enviar el resultado

        await mensaje_ping.edit(content=f'Pong! 🏓\nLatencia del bot: {bot_latencia} ms\nTu ping estimado: {ping_final} ms\n{critica}')

def setup(bot):
    bot.add_cog(Ping(bot))
