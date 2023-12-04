import discord
from discord.ext import commands
import random

class Saludos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def saludar(self, ctx, *, comando: str = None):
        respuestas_personalizadas = {
            'hola': ['¡Hola, humano!', '¿Qué tal estás?', '¡Saludos!'],
            'buenosdias': ['Buenos días, humano.', '¡La mañana es el mejor momento del día!', '¡Buen día!'],
            'buenasnoches': ['Buenas noches, duerme bien.', '¡Hasta mañana!', 'Que tengas dulces sueños.']
        }

        if comando is None or comando.lower() not in respuestas_personalizadas:
            opciones_comandos = ', '.join(respuestas_personalizadas.keys())
            mensaje_ayuda = f'Por favor, proporciona un comando válido. Opciones: {opciones_comandos}'
            await ctx.send(mensaje_ayuda)
        else:
            respuesta = random.choice(respuestas_personalizadas[comando.lower()])
            await ctx.send(f'{ctx.author.mention}, {respuesta}')

def setup(bot):
    bot.add_cog(Saludos(bot))
