import random
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class Deleted_Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        # Prevent the bot from reacting to its own messages or responses
        if message.author == self.bot.user or message.reference:
            print("Ignorando mensaje propio o respuesta")
            return

        author_id = str(message.author.id)
        guild_id = str(message.guild.id)

        try:
            # Conexión a la base de datos
            db = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            cursor = db.cursor()

            # Check if the server is registered
            cursor.execute("SELECT guild_language, activated_events FROM server_settings WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if result is None:
                await message.channel.send("This server is not registered. Please contact the administrator.")
                cursor.close()
                db.close()
                return

            # Extract language from server and if events are activated
            language_id, activated_events_value = result
            print(f"Idioma del servidor: {language_id}, Eventos activados: {activated_events_value}")

            message_probability = random.randint(1,5)

            if message_probability == 1:
                # Check if events are activated
                if activated_events_value == 1:
                    
                    
                    # Get a random delete event message
                    cursor.execute("""
                        SELECT message FROM event_message 
                        WHERE type_id = 4 AND language_id = %s
                        ORDER BY RAND() LIMIT 1
                    """, (language_id,))
                    deleted_result = cursor.fetchone()

                    # Check the language and send the response
                    if language_id == 1:
                        message_content = deleted_result[0] if deleted_result else "Deleting data?"
                    elif language_id == 2:
                        message_content = deleted_result[0] if deleted_result else "¿Eliminando datos?"

                    await message.channel.send(message_content.format(user_mention=message.author.mention))
            else:
                return

            
            cursor.close()
            db.close()

        except mysql.connector.Error as err:
            print(f"Error en la base de datos: {err}")
            await message.channel.send("An error occurred while processing your request.")
        except Exception as e:
            print(f"Error inesperado: {e}")
            await message.channel.send("An unexpected error occurred.")
