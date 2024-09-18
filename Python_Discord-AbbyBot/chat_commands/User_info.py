import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="user_info", description="Get user information")
    @app_commands.describe(member="The user you want to get information about")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        # If no member is mentioned, default to the user who invoked the command
        if member is None:
            member = interaction.user

        # Connect to the database using environment variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # AbbyBot ID for her Picture
        bot_id = 1028065784016142398  # AbbyBot ID

        async def get_bot_avatar():
            # Fetch the bot's user object using the bot_id
            bot_user = await self.bot.fetch_user(bot_id)
            # Now you can access the avatar URL
            bot_avatar_url = bot_user.display_avatar.url
            return bot_avatar_url

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

        # Process language-specific logic
        language_id = result[0]  # The language ID from the query

        # Query to get user information from the database
        user_info_query = """
        SELECT u.user_username, u.user_nickname, u.user_birthday, u.is_active, u.is_admin, u.is_bot, u.user_privilege, p.privilege_name
        FROM dashboard u
        JOIN privileges p ON u.user_privilege = p.value
        WHERE u.guild_id = %s AND u.user_id = %s;
        """

        cursor.execute(user_info_query, (interaction.guild_id, member.id))
        user_info = cursor.fetchone()

        if user_info:
            username = user_info[0]
            user_nickname = user_info[1] if user_info[1] else member.nick
            user_birthday = user_info[2] if user_info[2] else "Unknown"
            is_active = "Yes" if user_info[3] else "No"
            is_admin = "Yes" if user_info[4] else "No"
            is_bot = "Yes" if user_info[5] else "No"
            privilege_value = user_info[6]  # Using privilege value (numeric)
            privilege_name = user_info[7]
        else:
            username = member.name
            user_nickname = member.nick
            user_birthday = "Unknown"
            is_active = "Unknown"
            is_admin = "Unknown"
            is_bot = "Unknown"
            privilege_value = 0
            privilege_name = "No privilege"

        # Get user roles from the database
        roles_query = """
        SELECT role_id, role_name 
        FROM user_roles 
        WHERE guild_id = %s AND user_id = %s;
        """
        cursor.execute(roles_query, (interaction.guild_id, member.id))
        roles_result = cursor.fetchall()

        roles = ', '.join([f"<@&{role[0]}>" for role in roles_result]) if roles_result else "No roles"

        # Get user Discord data (avatar, account creation date, joined date)
        avatar_url = member.display_avatar.url
        user_id = member.id
        created_at = member.created_at.strftime("%B %d, %Y")
        joined_at = member.joined_at.strftime("%B %d, %Y") if member.joined_at else "Unknown"

        # Check for Nitro via Server Boosting
        has_nitro = "Yes" if member.premium_since else "No"

        # Check for badges (requires Discord.py v2.0+)
        badges = [badge.name for badge in member.public_flags.all()] if member.public_flags else []

        # Embed colors based on privilege_value (numeric value)
        color = {
            1: 0x00FF00,  # Green for Normal User
            2: 0xFFFF00,  # Yellow for Wishlist Contributor
            3: 0xFFA500,  # Orange for Developer Contributor
            4: 0xFF0000,  # Red for Project Owner
            5: 0xb45428   # AbbyBot color
        }.get(privilege_value, 0x808080)  # Default to grey if privilege_value is not found

        # Construct the embed based on the server language
        if language_id == 1:  # English
            embed = discord.Embed(title=f"User Information for {username}", color=color)
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name="Username", value=username, inline=True)
            embed.add_field(name="User Nickname", value=user_nickname, inline=True)  # Nickname included
            embed.add_field(name="User ID", value=user_id, inline=True)
            embed.add_field(name="Account Created", value=created_at, inline=True)
            embed.add_field(name="Joined Server", value=joined_at, inline=True)
            embed.add_field(name="Server Booster", value=has_nitro, inline=True)
            embed.add_field(name="Badges", value=", ".join(badges) if badges else "No badges", inline=True)
            embed.add_field(name="AbbyBot Privilege", value=privilege_name, inline=True)
            embed.add_field(name="User Birthday", value=user_birthday, inline=True)
            embed.add_field(name="Is Active?", value=is_active, inline=True)
            embed.add_field(name="Is Admin?", value=is_admin, inline=True)
            embed.add_field(name="Is Bot?", value=is_bot, inline=True)
            embed.add_field(name="Roles", value=roles, inline=True)

        elif language_id == 2:  # Spanish
            embed = discord.Embed(title=f"Información del Usuario {username}", color=color)
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name="Nombre de usuario", value=username, inline=True)
            embed.add_field(name="Apodo", value=user_nickname, inline=True)  # Nickname included
            embed.add_field(name="ID de usuario", value=user_id, inline=True)
            embed.add_field(name="Cuenta creada", value=created_at, inline=True)
            embed.add_field(name="Se unió al servidor", value=joined_at, inline=True)
            embed.add_field(name="Impulsor del servidor", value="Sí" if has_nitro == "Yes" else "No", inline=True)
            embed.add_field(name="Insignias", value=", ".join(badges) if badges else "Sin insignias", inline=True)
            embed.add_field(name="Privilegio de AbbyBot", value=privilege_name, inline=True)
            embed.add_field(name="Fecha de Cumpleaños", value=user_birthday, inline=True)
            embed.add_field(name="Está Activo?", value=is_active, inline=True)
            embed.add_field(name="Es Admin?", value=is_admin, inline=True)
            embed.add_field(name="Es Bot?", value=is_bot, inline=True)
            embed.add_field(name="Roles", value=roles, inline=True)

        # Get the bot's avatar (must use await since it's an async function)
        bot_avatar_url = await get_bot_avatar()

        embed.set_footer(
            text="AbbyBot",  # AbbyBot name
            icon_url=bot_avatar_url  # AbbyBot picture
        )

        # Send the embed
        await interaction.response.send_message(embed=embed)

        # Close the database connection
        cursor.close()
        db.close()
