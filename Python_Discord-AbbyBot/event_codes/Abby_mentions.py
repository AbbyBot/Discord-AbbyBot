import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

# Load dotenv variables
load_dotenv()

class Abby_mentions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        # Prevent the bot from mentioning itself or responding to replies
        if message.author == self.bot.user or message.reference:
            return

        # Check if the bot was mentioned directly with @
        if self.bot.user in message.mentions:

            author_id = str(message.author.id)
            guild_id = str(message.guild.id)

            # Database connection
            db = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            cursor = db.cursor()

            # Check if the server is registered
            cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()

            if result is None:
                await message.channel.send("This server is not registered. Please contact the administrator.")
                cursor.close()
                db.close()
                return

            # Get the server language ID
            language_id = result[0]

            # Check if events are activated or deactivated
            cursor.execute("SELECT activated_events FROM server_settings WHERE guild_id = %s", (guild_id,))
            activated_events_value = cursor.fetchone()

            # Access the actual value from the tuple
            if activated_events_value and activated_events_value[0] == 1:

                # Check if a user record already exists on this server
                cursor.execute("""
                    SELECT mention_count, last_mention FROM mention_counter 
                    WHERE user_id = %s AND user_server = %s
                """, (author_id, guild_id))
                mention_record = cursor.fetchone()

                if mention_record:
                    mention_count = mention_record[0] + 1
                else:
                    mention_count = 1

                # Update or insert the mention counter
                if mention_record:
                    cursor.execute("""
                        UPDATE mention_counter 
                        SET mention_count = %s, last_mention = %s 
                        WHERE user_id = %s AND user_server = %s
                    """, (mention_count, datetime.now(), author_id, guild_id))
                else:
                    cursor.execute("""
                        INSERT INTO mention_counter (user_id, user_server, mention_count, last_mention)
                        VALUES (%s, %s, %s, %s)
                    """, (author_id, guild_id, mention_count, datetime.now()))

                db.commit()

                # Check counter status
                if mention_count > 7:
                    # "forgive" answer
                    cursor.execute("""
                        SELECT message FROM event_message 
                        WHERE type_id = 3 AND language_id = %s
                        ORDER BY RAND() LIMIT 1
                    """, (language_id,))
                    forgiveness_result = cursor.fetchone()

                    if language_id == 1:
                        message_content = forgiveness_result[0] if forgiveness_result else "I forgive you this time."
                    elif language_id == 2:
                        message_content = forgiveness_result[0] if forgiveness_result else "Te perdono esta vez."
                    else:
                        message_content = forgiveness_result[0] if forgiveness_result else "I forgive you this time."

                    await message.channel.send(message_content.format(user_mention=message.author.mention))

                    # Reset counter
                    cursor.execute("""
                        UPDATE mention_counter 
                        SET mention_count = 0, last_mention = %s 
                        WHERE user_id = %s AND user_server = %s
                    """, (datetime.now(), author_id, guild_id))

                    db.commit()
                    cursor.close()
                    db.close()
                    return

                elif mention_count > 3:

                    # "angry" answer
                    cursor.execute("""
                        SELECT message FROM event_message 
                        WHERE type_id = 2 AND language_id = %s
                        ORDER BY RAND() LIMIT 1
                    """, (language_id,))
                    angry_result = cursor.fetchone()

                    if language_id == 1:
                        message_content = angry_result[0] if angry_result else "You're bothering me too much!"
                    elif language_id == 2:
                        message_content = angry_result[0] if angry_result else "¡Me estás molestando demasiado!"
                    else:
                        message_content = angry_result[0] if angry_result else "You're bothering me too much!"

                    await message.channel.send(message_content.format(user_mention=message.author.mention))
                    cursor.close()
                    db.close()
                    return

                # "normal" answer
                cursor.execute("""
                    SELECT message FROM event_message 
                    WHERE type_id = 1 AND language_id = %s
                    ORDER BY RAND() LIMIT 1
                """, (language_id,))
                normal_result = cursor.fetchone()

                if language_id == 1:
                    message_content = normal_result[0] if normal_result else "Right now I don't know how to answer you :/"
                elif language_id == 2:
                    message_content = normal_result[0] if normal_result else "Ahora mismo no sé cómo responderte :/"
                else:
                    message_content = normal_result[0] if normal_result else "Right now I don't know how to answer you :/"

                await message.channel.send(message_content.format(user_mention=message.author.mention))

                # Close DB
                cursor.close()
                db.close()
                
            # Deactivated events
            else:
                return


async def setup(bot):
    await bot.add_cog(Abby_mentions(bot))
