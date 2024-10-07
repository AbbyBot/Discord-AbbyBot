import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class ServerCommands(commands.GroupCog, name="server"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="Check server info.")
    async def server_info(self, interaction: discord.Interaction):

        # Connect to the database with dotenv variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get guild_id from the interaction
        guild_id = interaction.guild_id


        bot_id = 1028065784016142398  # AbbyBot ID

        async def get_bot_avatar():
            bot_user = await self.bot.fetch_user(bot_id)
            bot_avatar_url = bot_user.display_avatar.url
            return bot_avatar_url

        # Fetch server information from database
        server_data_query = """
            SELECT s.guild_name, s.member_count, s.guild_language, p.user_username, d.user_server_nickname
            FROM server_settings s
            JOIN dashboard d ON s.guild_id = d.guild_id
            JOIN user_profile p ON d.user_profile_id = p.id
            WHERE s.guild_id = %s
            AND s.owner_id = p.user_id;

        """
        cursor.execute(server_data_query, (guild_id,))
        result_data = cursor.fetchone()

        if result_data:
            guild_name = result_data[0]
            member_count = result_data[1]
            guild_language = result_data[2]
            owner_username = result_data[3]
            owner_nickname = result_data[4]
        else:
            await interaction.response.send_message("Could not retrieve server information.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # Fetch the server icon using Discord.py
        guild = interaction.guild
        guild_icon_url = guild.icon.url if guild.icon else None

        # Language handling for embeds
        if guild_language == 1:  # English
            embed = discord.Embed(
                title=f"Server Information for {guild_name}",
                description=f"Here are some details for the server **{guild_name}**:",
                color=discord.Color.orange()
            )
            embed.add_field(name="Owner Username", value=owner_username, inline=True)
            embed.add_field(name="Owner Nickname", value=owner_nickname, inline=True)
            embed.add_field(name="Member Count", value=member_count, inline=True)
            embed.add_field(name="Language", value="English", inline=True)

        elif guild_language == 2:  # Spanish
            embed = discord.Embed(
                title=f"Información del Servidor {guild_name}",
                description=f"Aquí están algunos detalles del servidor **{guild_name}**:",
                color=discord.Color.orange()
            )
            embed.add_field(name="Nombre de Usuario del Propietario", value=owner_username, inline=True)
            embed.add_field(name="Apodo del Propietario", value=owner_nickname, inline=True)
            embed.add_field(name="Cantidad de Miembros", value=member_count, inline=True)
            embed.add_field(name="Idioma", value="Español", inline=True)

        # Add server icon if available
        if guild_icon_url:
            embed.set_thumbnail(url=guild_icon_url)

        
        bot_avatar_url = await get_bot_avatar()

        embed.set_footer(
            text="AbbyBot",  
            icon_url=bot_avatar_url  
        )

        # Send the embed
        await interaction.response.send_message(embed=embed)

        # Close the database connection
        cursor.close()
        db.close()


