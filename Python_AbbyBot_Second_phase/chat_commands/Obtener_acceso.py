import discord
from discord.ext import commands


#Obtener_acceso.py se encargará de asignar roles mediante reacciones


class ObtenerAcceso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1183519805119135744  # Reemplaza con el ID del canal
        self.id_rol_1 = 1183517668544888843   # Reemplaza con el ID del primer rol
        self.id_rol_2 = 1181047311263072287   # Reemplaza con el ID del segundo rol
        self.message_id = None  # Inicialmente, el ID del mensaje está vacío

    @commands.command()
    async def obtener_acceso(self, ctx):
        # Verificar si el mensaje ya está fijado
        if not self.message_id:
            # Crear un mensaje de embed
            embed = discord.Embed(
                title="Obtener Acceso",
                description="Reacciona con los emojis correspondientes para obtener acceso a los canales.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Roles de programador/a", value=":one: Si eres programador/a y estás interesando en los canales de programación", inline=False)
            embed.add_field(name="Roles de AbbyBot dev", value=":two: ¿Te interesa contribuir en el desarrollo de AbbyBot?", inline=False)
            embed.set_footer(text="Siempre podrás agregar y quitarte un rol si ya no lo quieres.")

            # Enviar el mensaje y fijarlo
            message = await ctx.send(embed=embed)
            await message.pin()
            self.message_id = message.id  # Almacenar el ID del mensaje fijado

            # Agregar reacciones
            emojis = ['1️⃣', '2️⃣']  # Puedes agregar más emojis según sea necesario
            for emoji in emojis:
                await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Verificar que la reacción se hizo en el canal correcto y que el usuario no es un bot
        if reaction.message.channel.id == self.channel_id and user.id != self.bot.user.id:
            # Verificar si el mensaje es el correcto
            if reaction.message.id == self.message_id:
                # Verificar qué emoji se usó y asignar el rol correspondiente
                if str(reaction.emoji) == '1️⃣':
                    await self.asignar_rol(user, self.id_rol_1)
                elif str(reaction.emoji) == '2️⃣':
                    await self.asignar_rol(user, self.id_rol_2)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        # Verificar que la reacción se hizo en el canal correcto y que el usuario no es un bot
        if reaction.message.channel.id == self.channel_id and user.id != self.bot.user.id:
            # Verificar si el mensaje es el correcto
            if reaction.message.id == self.message_id:
                # Verificar qué emoji se usó y quitar el rol correspondiente
                if str(reaction.emoji) == '1️⃣':
                    await self.quitar_rol(user, self.id_rol_1)
                elif str(reaction.emoji) == '2️⃣':
                    await self.quitar_rol(user, self.id_rol_2)

    async def asignar_rol(self, user, id_rol):
        # Obtener el rol por su ID
        rol = user.guild.get_role(id_rol)
        if rol:
            await user.add_roles(rol)

    async def quitar_rol(self, user, id_rol):
        # Obtener el rol por su ID
        rol = user.guild.get_role(id_rol)
        if rol:
            await user.remove_roles(rol)

# Asegúrate de configurar CHANNEL_ID, ID_ROL_1 e ID_ROL_2 correctamente
# Los valores se han movido dentro de la clase como atributos de instancia
# para que puedan ser accesibles desde los métodos de la clase.

# Resto del código para inicializar el bot y cargar la extensión...
