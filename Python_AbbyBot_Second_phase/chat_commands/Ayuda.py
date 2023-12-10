import discord
from discord.ext import commands
import asyncio
import random

class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ayuda(self, ctx):
        mensaje_ping = await ctx.send("Estamos trabajando en ello...")



def setup(bot):
    bot.add_cog(Ayuda(bot))
