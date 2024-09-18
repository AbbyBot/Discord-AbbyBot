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
        bot_id = 1230325124411035709  # AbbyBot ID

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

        # Get the mentioned user's information
        avatar_url = member.display_avatar.url
        username = member.name
        user_id = member.id
        created_at = member.created_at.strftime("%B %d, %Y")
        joined_at = member.joined_at.strftime("%B %d, %Y") if member.joined_at else "Unknown"

        # Check for Nitro via Server Boosting
        has_nitro = "Yes" if member.premium_since else "No"

        # Check for other badges (requires Discord.py v2.0+)
        badges = [badge.name for badge in member.public_flags.all()] if member.public_flags else []

        # Get database info
        privilege_query = """
        SELECT u.user_birthday, u.is_admin, u.is_bot, p.privilege_name, p.value
        FROM dashboard u
        JOIN privileges p ON u.user_privilege = p.value
        WHERE u.guild_id = %s AND u.user_id = %s;
        """
        # Get user roles
        roles_query = """
        SELECT role_id, role_name 
        FROM user_roles 
        WHERE guild_id = %s AND user_id = %s;
        """

        # Execute Query before result
        cursor.execute(privilege_query, (interaction.guild_id, member.id))
        privilege_result = cursor.fetchone()

        # Execute Role Query before result
        cursor.execute(roles_query, (interaction.guild_id, member.id))
        roles_result = cursor.fetchall()

        user_birthday = privilege_result[0]                
        is_admin = privilege_result[1]           
        is_bot = privilege_result[2]                
        privilege_name = privilege_result[3]     
        privilege_value = privilege_result[4] 


        # Roles result processing (list of roles)
        roles = ', '.join([f"<@&{role[0]}>" for role in roles_result]) if roles_result else "No roles"

        # Embed colors

        if privilege_value == 1:
            color = 0x00FF00  # Green Normal Users
        elif privilege_value == 2:
            color = 0xFFFF00  # Yellow Wishlist Contributor
        elif privilege_value == 3:
            color = 0xFFA500  # Orange Developer Contributor
        elif privilege_value == 4:
            color = 0xFF0000  # Red Project Owner
        elif privilege_value == 5:
            color = 0xb45428  # AbbyBot color
        else:
            color = 0x808080 # Grey color

        # Construct the embed
        if language_id == 1:  # English
            embed = discord.Embed(title=f"User Information for {username}", color=color)
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name="Username", value=username, inline=True)
            embed.add_field(name="User ID", value=user_id, inline=True)
            embed.add_field(name="Account Created", value=created_at, inline=True)
            embed.add_field(name="Joined Server", value=joined_at, inline=True)
            embed.add_field(name="Server Booster", value=has_nitro, inline=True)
            embed.add_field(name="Badges", value=", ".join(badges) if badges else "No badges", inline=True)
            embed.add_field(name="AbbyBot Privilege", value=privilege_name, inline=True)
            if user_birthday is None:
                embed.add_field(name="User Birthday", value="Unknown", inline=True)
            else:
                embed.add_field(name="User Birthday", value=user_birthday, inline=True)
            embed.add_field(name=f"{username} has admin on server?", value="Yes" if is_admin == 1 else "No", inline=True)
            embed.add_field(name=f"{username} are a bot?", value="Yes" if is_bot == 1 else "No", inline=True)
            embed.add_field(name="Roles", value=roles, inline=True)

        elif language_id == 2:  # Spanish
            embed = discord.Embed(title=f"Información del Usuario {username}", color=color)
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name="Nombre de usuario", value=username, inline=True)
            embed.add_field(name="ID de usuario", value=user_id, inline=True)
            embed.add_field(name="Cuenta creada", value=created_at, inline=True)
            embed.add_field(name="Se unió al servidor", value=joined_at, inline=True)
            embed.add_field(name="Impulsor del servidor", value="Sí" if has_nitro == "Yes" else "No", inline=True)
            embed.add_field(name="Insignias", value=", ".join(badges) if badges else "Sin insignias", inline=True)
            embed.add_field(name="Privilegio de AbbyBot", value=f"**{privilege_name}**", inline=True)
            if user_birthday is None:
                embed.add_field(name="Fecha de Cumpleaños", value="Desconocida", inline=True)
            else:
                embed.add_field(name="Fecha de Cumpleaños", value=user_birthday, inline=True)
            embed.add_field(name=f"{username} es admin en el servidor?", value="Si" if is_admin == 1 else "No", inline=True)
            embed.add_field(name=f"{username} es un bot?", value="Si" if is_bot == 1 else "No", inline=True)
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
