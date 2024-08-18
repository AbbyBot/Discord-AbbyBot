import discord
from discord.ext import commands
import sqlite3

# Base de datos
conn = sqlite3.connect('abby_database.db')
cursor = conn.cursor()

class Banned_URLs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Verificar si el mensaje proviene de un usuario y contiene una URL
        if message.author.bot or not message.content.startswith('http'):
            return

        # Verificar si la URL está en la lista de imágenes prohibidas
        cursor.execute("SELECT * FROM banned_images WHERE url = ?", (message.content,))
        banned_image = cursor.fetchone()

        if banned_image:
            # Obtener el ID del usuario y verificar si ya tiene advertencias
            user_id = str(message.author.id)
            cursor.execute("SELECT * FROM user_warnings WHERE discord_user_id = ?", (user_id,))
            user_warnings = cursor.fetchone()

            # Inicializar new_warn_count
            new_warn_count = 0

            if user_warnings:
                # Obtener el contador de advertencias existente
                existing_warn_count = user_warnings[2]

                # Incrementar el contador de advertencias
                new_warn_count = existing_warn_count + 1

                # Actualizar el contador de advertencias en la base de datos
                cursor.execute("UPDATE user_warnings SET warn_count = ? WHERE discord_user_id = ?", (new_warn_count, user_id))
            else:
                # Insertar un nuevo registro para el usuario en la tabla de advertencias
                cursor.execute("INSERT INTO user_warnings (discord_user_id, warn_count) VALUES (?, 1)", (user_id,))
                new_warn_count = 1  # Configurar new_warn_count a 1 para la primera advertencia

            # Enviar mensaje de advertencia al usuario
            await message.author.send(f"¡Cuidado! Has enviado una imagen prohibida. Tu contador de advertencias es {new_warn_count}.")

            # Verificar si el usuario ha alcanzado 3 advertencias
            if new_warn_count >= 3:
                # Kickear al usuario del servidor
                await message.author.kick(reason="Alcanzó 3 advertencias.")
                
                await message.author.send(f"¡Aviso! Has llegado al límite de advertencias. Tu contador de advertencias es {new_warn_count}, has sido kickeado del grupo.")

                # Reiniciar el contador de advertencias del usuario
                cursor.execute("UPDATE user_warnings SET warn_count = 0 WHERE discord_user_id = ?", (user_id,))

            # Eliminar el mensaje del usuario después de las verificaciones
            await message.delete()

        # Guardar los cambios en la base de datos
        conn.commit()

def setup(bot):
    bot.add_cog(Banned_URLs(bot))
