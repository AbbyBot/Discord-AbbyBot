import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os
from embeds.embeds import account_inactive_embed  # import embed system
from datetime import datetime

# Load dotenv variables
load_dotenv()

class SetCommands(commands.GroupCog, name="set"):
    def __init__(self, bot):
        self.bot = bot

    async def check_user_is_active(self, interaction, user_id):
        # Connect to the database
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Check if the user is active (is_active = 1) or inactive (is_active = 0)
        cursor.execute("SELECT is_active FROM user_profile WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()

        # Close the database connection
        cursor.close()
        db.close()

        if result is None:
            await interaction.response.send_message("User not found in the database.", ephemeral=True)
            return False
        elif result[0] == 0:
            try:
                # Send an embed and notify the user
                embed, file = account_inactive_embed()
                await interaction.user.send(embed=embed, file=file)
            except discord.Forbidden:
                print(f"Could not send DM to {interaction.user}. They may have DMs disabled.")

            await interaction.response.send_message(
                "Request Rejected: Your account has been listed as **inactive** in the AbbyBot system, please check your DM.",
                ephemeral=True)
            return False
        return True

    # Set birthday channel subcommand
    @app_commands.command(name="birthday_channel", description="Assign a channel so AbbyBot can celebrate users' birthdays.")
    async def set_birthday_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        user_id = interaction.user.id
        guild_id = interaction.guild_id

        # Check if user is active
        if not await self.check_user_is_active(interaction, user_id):
            return

        # Connect to the database
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Check the server's language setting
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        current_language_id = cursor.fetchone()[0]

        # Update the birthday channel
        cursor.execute("UPDATE server_settings SET birthday_channel = %s WHERE guild_id = %s;", (channel.id, guild_id))
        db.commit()

        # Confirm to the user
        if current_language_id == 1:
            await interaction.response.send_message(f"Birthday channel has been set to {channel.mention}.", ephemeral=True)
        elif current_language_id == 2:
            await interaction.response.send_message(f"El canal de cumpleaños se ha configurado en {channel.mention}.", ephemeral=True)

        # Close the database connection
        cursor.close()
        db.close()

    # Set logs channel subcommand
    @app_commands.command(name="logs_channel", description="Assign a channel for AbbyBot to send logs of server actions.")
    async def set_logs_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        user_id = interaction.user.id
        guild_id = interaction.guild_id

        # Check if user is active
        if not await self.check_user_is_active(interaction, user_id):
            return

        # Connect to the database
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Check the server's language setting
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        current_language_id = cursor.fetchone()[0]

        # Update the logs channel
        cursor.execute("UPDATE server_settings SET logs_channel = %s WHERE guild_id = %s;", (channel.id, guild_id))
        db.commit()

        # Confirm to the user
        if current_language_id == 1:
            await interaction.response.send_message(f"Logs channel has been set to {channel.mention}.", ephemeral=True)
        elif current_language_id == 2:
            await interaction.response.send_message(f"El canal de logs se ha configurado en {channel.mention}.", ephemeral=True)

        # Close the database connection
        cursor.close()
        db.close()

    # Prefix subcommand
    @app_commands.command(name="prefix", description="Change AbbyBot's prefix")
    async def set_prefix(self, interaction: discord.Interaction, prefix: str = None):
        user_id = interaction.user.id
        guild_id = interaction.guild_id

        # Check if user is active
        if not await self.check_user_is_active(interaction, user_id):
            return

        # Connect to the database
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get the server's language
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()
        current_language_id = result[0]

        # Check if a new prefix was provided
        if prefix is None:
            if current_language_id == 1:
                await interaction.response.send_message("Please provide the new prefix for AbbyBot.", ephemeral=True)
            elif current_language_id == 2:
                await interaction.response.send_message("Por favor proporcione el nuevo prefijo para AbbyBot.", ephemeral=True)
            return

        # Update the prefix in the database
        cursor.execute("UPDATE server_settings SET prefix = %s WHERE guild_id = %s;", (prefix, guild_id))
        db.commit()

        # Confirm to the user
        if current_language_id == 1:
            await interaction.response.send_message(f"Prefix has been changed to {prefix}.", ephemeral=True)
        elif current_language_id == 2:
            await interaction.response.send_message(f"El prefijo ha sido cambiado a {prefix}.", ephemeral=True)

        # Close the database connection
        cursor.close()
        db.close()

    # Set language Subcommand
    @app_commands.command(name="language", description="Set the language for this server.")
    @app_commands.choices(language=[
        discord.app_commands.Choice(name="English", value=1),  # 1 en
        discord.app_commands.Choice(name="Español", value=2)  # 2 es
    ])
    async def set_language(self, interaction: discord.Interaction, language: int):
        user_id = interaction.user.id
        guild_id = interaction.guild_id

        # Check if user is active
        if not await self.check_user_is_active(interaction, user_id):
            return

        # Connect to the database
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Update the language in the database
        cursor.execute("UPDATE server_settings SET guild_language = %s WHERE guild_id = %s;", (language, guild_id))
        db.commit()

        # Confirm to the user
        if language == 1:
            await interaction.response.send_message("The language has been set to English.", ephemeral=False)
        elif language == 2:
            await interaction.response.send_message("El idioma ha sido cambiado a Español.", ephemeral=False)

        # Close the database connection
        cursor.close()
        db.close()

    # Set birthday user Subcommand
    @app_commands.command(name="birthday", description="Set your birthday and AbbyBot will greet you on your birthday.")
    async def set_birthday(self, interaction: discord.Interaction, month: int, day: int, year: int):
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

        # Check if user is active
        if not await self.check_user_is_active(interaction, user_id):
            return

        # Validate that the year has exactly 4 digits
        if len(str(year)) != 4:
            if language_id == 1:
                await interaction.response.send_message("Error: The year must have 4 digits. Please enter a valid year.", ephemeral=True)
            else:
                await interaction.response.send_message("Error: El año debe tener 4 dígitos. Por favor ingresa un año válido.", ephemeral=True)
            return

        try:
            user_birthday_date = datetime(year, month, day)
            
            cursor.execute("UPDATE user_profile SET user_birthday = %s WHERE user_id = %s;", (user_birthday_date, user_id))
            db.commit()

            # Send response based on the language setting
            if language_id == 1:
                await interaction.response.send_message(f"Your birthday has been set to {user_birthday_date.strftime('%B %d, %Y')}. AbbyBot will greet you on this server or anywhere else where you are with me!", ephemeral=True)
            else:
                await interaction.response.send_message(f"Tu fecha de cumpleaños ha sido asignada el {user_birthday_date.strftime('%d de %B de %Y')}. ¡AbbyBot te saludará en este servidor o en cualquier otro donde estés junto a mi!", ephemeral=True)

        except ValueError as e:
            # If the values do not form a valid date
            if language_id == 1:
                await interaction.response.send_message(f"Error. Make sure you enter a valid date.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Error: {str(e)}. Asegúrate de ingresar una fecha válida.", ephemeral=True)

        # Close the database connection
        cursor.close()
        db.close()

