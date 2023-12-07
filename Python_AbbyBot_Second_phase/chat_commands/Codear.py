from discord.ext import commands

class Codear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def codear(self, ctx, *, codigo):
        await ctx.message.delete() # eliminar el mensaje del user
        # Envia el mensaje con el código formateado
        await ctx.send(f"```\n{codigo}\n```")

# Agrega el cog al bot
def setup(bot):
    bot.add_cog(Codear(bot))
