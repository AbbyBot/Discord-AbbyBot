import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime
import os

# Load dotenv variables
load_dotenv()

class SetBirthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_birthday", description="Set your birthday and AbbyBot will greet you on your birthday.")
    async def command_name(self, interaction: discord.Interaction, month: int, day: int, year: int):
        # Connect to the database using environment variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get guild_id from the interaction (server ID)
        guild_id = interaction.guild_id

        # Query to check the server's language setting (obligatory field)
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        user_id = interaction.user.id  # Get discord user id
        language_id = result[0]  # The language ID from the query

        # Validate that the year has exactly 4 digits
        if len(str(year)) != 4:
            if language_id == 1:
                await interaction.response.send_message("Error: The year must have 4 digits. Please enter a valid year.", ephemeral=True)
            else:
                await interaction.response.send_message("Error: El año debe tener 4 dígitos. Por favor ingresa un año válido.", ephemeral=True)
            return

        try:
            user_birthday_date = datetime(year, month, day)
            
            cursor.execute("UPDATE abbybot.dashboard SET user_birthday = %s WHERE user_id = %s;", (user_birthday_date, user_id))
            db.commit()

            # Send response based on the language setting
            if language_id == 1:
                await interaction.response.send_message(f"Your birthday has been set to {user_birthday_date.strftime('%B %d, %Y')}. AbbyBot will greet you on this server or by DM!", ephemeral=True)
            else:
                await interaction.response.send_message(f"Tu fecha de cumpleaños ha sido asignada el {user_birthday_date.strftime('%d de %B de %Y')}. ¡AbbyBot te saludará en este servidor o por DM!", ephemeral=True)

        except ValueError as e:
            # If the values do not form a valid date
            if language_id == 1:
                await interaction.response.send_message(f"Error. Make sure you enter a valid date.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Error. Asegúrate de ingresar una fecha válida.", ephemeral=True)


        # Close the database connection
        cursor.close()
        db.close()
