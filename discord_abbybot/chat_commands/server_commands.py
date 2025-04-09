import discord
from discord.ext import commands
from discord import app_commands
import os
from utils.db_utils import get_db_connection


class ServerCommands(commands.GroupCog, name="server"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="Check the information of a guild.")
    async def server_info(self, interaction: discord.Interaction):
        db, cursor = get_db_connection()

        # Get guild_id from the interaction
        guild_id = interaction.guild_id

        # Fetch server information from the database
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
            await interaction.response.send_message(
                "Could not retrieve server information.", ephemeral=True
            )
            cursor.close()
            db.close()
            return

        # Fetch the server details
        guild = interaction.guild
        guild_icon_url = guild.icon.url if guild.icon else None
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        roles = len(guild.roles)
        
        if guild_language == 2:  # Spanish
            created_at = guild.created_at.strftime("%d-%m-%Y %H:%M:%S")
            afk_timeout = f"{guild.afk_timeout // 60} minutos" if guild.afk_timeout else "Ninguno"
            verification_level = {
            "None": "Ninguno",
            "Low": "Bajo",
            "Medium": "Medio",
            "High": "Alto",
            "Very_high": "Muy Alto"
            }.get(guild.verification_level.name, "Desconocido")
        else:
            created_at = guild.created_at.strftime("%Y-%m-%d %H:%M:%S")
            afk_timeout = f"{guild.afk_timeout // 60} minutes" if guild.afk_timeout else "None"
            verification_level = guild.verification_level.name.capitalize()
        
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        emoji_count = len(guild.emojis)
        sticker_count = len(guild.stickers)
        afk_channel = guild.afk_channel.name if guild.afk_channel else "None"

        # Determine language for the embed
        if guild_language == 1:  # English
            embed_title = f"Server Information for {guild_name}"
            embed_description = f"Here are some details for the server **{guild_name}**:"
            language_name = "English"
            fields = {
                "Owner Username": owner_username,
                "Owner Nickname": owner_nickname,
                "Member Count": member_count,
                "Text Channels": text_channels,
                "Voice Channels": voice_channels,
                "Roles": roles,
                "Created At": created_at,
                "Boost Level": boost_level,
                "Boost Count": boost_count,
                "Verification Level": verification_level,
                "Emoji Count": emoji_count,
                "Sticker Count": sticker_count,
                "AFK Channel": afk_channel,
                "AFK Timeout": afk_timeout,
                "AbbyBot's Language": language_name,
            }
        elif guild_language == 2:  # Spanish
            embed_title = f"Información del Servidor {guild_name}"
            embed_description = f"Aquí están algunos detalles del servidor **{guild_name}**:"
            language_name = "Español"
            fields = {
                "Nombre del Propietario": owner_username,
                "Apodo del Propietario": owner_nickname,
                "Cantidad de Miembros": member_count,
                "Canales de Texto": text_channels,
                "Canales de Voz": voice_channels,
                "Roles": roles,
                "Creado El": created_at,
                "Nivel de Boost": boost_level,
                "Cantidad de Boosts": boost_count,
                "Nivel de Verificación": verification_level,
                "Cantidad de Emojis": emoji_count,
                "Cantidad de Stickers": sticker_count,
                "Canal AFK": afk_channel,
                "Tiempo AFK": afk_timeout,
                "Idioma de AbbyBot": language_name,
            }
        else:
            embed_title = f"Server Information for {guild_name}"
            embed_description = f"Here are some details for the server **{guild_name}**:"
            language_name = "Unknown"
            fields = {
                "Owner Username": owner_username,
                "Owner Nickname": owner_nickname,
                "Member Count": member_count,
                "Text Channels": text_channels,
                "Voice Channels": voice_channels,
                "Roles": roles,
                "Created At": created_at,
                "Boost Level": boost_level,
                "Boost Count": boost_count,
                "Verification Level": verification_level,
                "Emoji Count": emoji_count,
                "Sticker Count": sticker_count,
                "AFK Channel": afk_channel,
                "AFK Timeout": afk_timeout,
                "AbbyBot's Language": language_name,
            }

        # Create the embed
        embed = discord.Embed(
            title=embed_title,
            description=embed_description,
            color=discord.Color.random()
        )

        # Add fields to the embed
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)

        # Add server icon as thumbnail (if available)
        if guild_icon_url:
            embed.set_thumbnail(url=guild_icon_url)

        # Add footer with AbbyBot branding
        footer_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "abbybot.png")
        footer_file = discord.File(footer_image_path, filename="abbybot.png")
        embed.set_footer(text="AbbyBot • Your Discord Ally", icon_url="attachment://abbybot.png")

        # Add buttons
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="AbbyBot Website", url="https://abbybotproject.com", style=discord.ButtonStyle.link))

        # Send the embed
        await interaction.response.send_message(embed=embed, files=[footer_file], view=view)

        # Close database connection
        cursor.close()
        db.close()


