import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os
from embeds.embeds import account_inactive_embed

# Load dotenv variables
load_dotenv()

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server_info", description="Check server info.")
    async def help(self, interaction: discord.Interaction):

        # Connect to database with dotenv variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Check if server is registered
        guild_id = interaction.guild_id
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()
        
        if result is None:
            # if server is not registered, send error message
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return
        
        # Get guild_id and user_id from the interaction
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        # Check if the user is active (is_active = 1) or inactive (is_active = 0)
        cursor.execute("SELECT is_active FROM user_profile WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("User not found in the database.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # If the user is inactive (is_active = 0), send an embed in DM and exit
        is_active = result[0]
        if is_active == 0:
            try:
                # Get the embed and file
                embed, file = account_inactive_embed()

                # Send the embed and the file as DM
                await interaction.user.send(embed=embed, file=file)
                
                print(f"User {interaction.user} is inactive and notified.")
            except discord.Forbidden:
                print(f"Could not send DM to {interaction.user}. They may have DMs disabled.")

            await interaction.response.send_message("Request Rejected: Your account has been listed as inactive in the AbbyBot system, please check your DM.", ephemeral=True)

            cursor.close()
            db.close()
            return


        server_data = """
            SELECT s.guild_name, d.user_username, d.user_nickname, COUNT(d2.id) as member_count, l.language_code
            FROM server_settings s
            JOIN dashboard d ON s.owner_id = d.user_id AND s.guild_id = d.guild_id -- Asegura que el nickname corresponde al servidor actual
            JOIN dashboard d2 ON s.guild_id = d2.guild_id AND d2.is_active = 1
            JOIN languages l ON s.guild_language = l.id
            WHERE s.guild_id = %s
            GROUP BY s.guild_name, d.user_username, d.user_nickname, l.language_code;
        """


        cursor.execute(server_data, (guild_id,))
        result_data = cursor.fetchall()


        if result_data:
            result_data = result_data[0]  # Use the first row (if you're expecting only one)
            guild_name = result_data[0]  # First column from the query
            owner_username = result_data[1]  # Second column from the query
            owner_nickname = result_data[2]  # Third column from the query
            member_count = result_data[3]  # Fourth column from the query
            language_code = result_data[4]  # Fifth column from the query


        # Get server language
        language_id = result[0]  # Get language ID

        if language_id == 1:
            description_title = 'Server info'
            description_text = f"Here is some data from the server {guild_name}"
        elif language_id == 2:
            description_title = 'Información del servidor'
            description_text = f"Aquí tiene algunos datos sobre el servidor {guild_name}"


        # Create embed
        embed = discord.Embed(
            title=description_title,
            description=description_text,
            color=discord.Color.from_rgb(145, 61, 33)  # Abbybot's color
        )

        # Create a embed with result_data variables

        embed.add_field(name="Server Name" if language_id == 1 else "Nombre del servidor", value=guild_name, inline=False)
        embed.add_field(name="Owner Username" if language_id == 1 else "Nombre de usuario del propietario", value=owner_username, inline=False)
        embed.add_field(name="Owner Nickname" if language_id == 1 else "Apodo del propietario", value=owner_nickname, inline=False)
        embed.add_field(name="Member Count" if language_id == 1 else "Cantidad de miembros", value=member_count, inline=False)
        embed.add_field(name="Language Code" if language_id == 1 else "Código de lenguaje", value=language_code, inline=False)


        await interaction.response.send_message(embed=embed)

        # Close db connection
        cursor.close()
        db.close()

# Add cog command
async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
