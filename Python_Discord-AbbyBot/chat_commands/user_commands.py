import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os
from embeds.embeds import account_inactive_embed  # import embed system
from utils.utils import get_bot_avatar

# Load dotenv variables
load_dotenv()

class UserCommands(commands.GroupCog, name="user"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="Get user information")
    @app_commands.describe(member="The user you want to get information about")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user

        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        bot_id = 1028065784016142398  # AbbyBot ID

        guild_id = interaction.guild_id

        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        language_id = result[0]  # The language ID from the query


        # Check if the user executing the command (interaction.user) is active or inactive
        user_id = interaction.user.id  
        cursor.execute("SELECT is_active FROM user_profile WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("User not found in the database.", ephemeral=True)
            cursor.close()
            db.close()
            return
        
        is_active = result[0]

        # If the person executing the command is inactive, send the DM to interaction.user
        if is_active == 0:
            try:
                # Get the embed and file for inactive users
                embed_inactive, file_inactive = await account_inactive_embed(self.bot)

                # Send embed to dm
                await interaction.user.send(embed=embed_inactive, file=file_inactive)
                
                print(f"User {interaction.user} is inactive and notified.")
            except discord.Forbidden:
                print(f"Could not send DM to {interaction.user}. They may have DMs disabled.")
            
            
            cursor.close()
            db.close()

            # Notify user is inactive
            await interaction.response.send_message(
                "Request Rejected: Your account has been listed as **inactive** in the AbbyBot system, please check your DM.",
                ephemeral=True
            )
            return
        

        # Query to get user information from the database, joining with user_profile
        user_info_query = """
        SELECT p.user_username, d.user_server_nickname, p.user_birthday, p.is_active, d.is_admin, d.is_bot, p.user_privilege, pr.privilege_name
        FROM dashboard d
        JOIN user_profile p ON d.user_profile_id = p.id
        JOIN privileges pr ON p.user_privilege = pr.id
        WHERE d.guild_id = %s AND p.user_id = %s;
        """

        cursor.execute(user_info_query, (interaction.guild_id, member.id))
        user_info = cursor.fetchone()

        if user_info:
            username = user_info[0]
            user_nickname = user_info[1] if user_info[1] else (member.display_name if member.display_name else member.name)
            user_birthday = user_info[2] if user_info[2] else "Unknown"
            
            # Formatting the date according to the language
            if user_birthday != "Unknown":
                if language_id == 1:
                    user_birthday = user_info[2].strftime("%B %d, %Y")  # English: Month, Day, Year
                elif language_id == 2:
                    user_birthday = user_info[2].strftime("%d de %B de %Y")  # Spanish: Day, Month, Year
            
            # Translation of values ​​according to language
            if language_id == 1:
                is_active = "Yes" if user_info[3] else "No"
                is_admin = "Yes" if user_info[4] else "No"
                is_bot = "Yes" if user_info[5] else "No"
            elif language_id == 2:
                is_active = "Sí" if user_info[3] else "No"
                is_admin = "Sí" if user_info[4] else "No"
                is_bot = "Sí" if user_info[5] else "No"

            privilege_value = user_info[6]
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
        WHERE guild_id = %s AND user_profile_id = (
            SELECT id FROM user_profile WHERE user_id = %s
        );
        """
        cursor.execute(roles_query, (interaction.guild_id, member.id))
        roles_result = cursor.fetchall()

        roles = ', '.join([f"<@&{role[0]}>" for role in roles_result]) if roles_result else "No roles"

        avatar_url = member.display_avatar.url
        user_id = member.id
        created_at = member.created_at.strftime("%B %d, %Y")
        joined_at = member.joined_at.strftime("%B %d, %Y") if member.joined_at else "Unknown"
        has_nitro = "Yes" if member.premium_since else "No"
        badges = [badge.name for badge in member.public_flags.all()] if member.public_flags else []

        color = {
            1: 0x00FF00,
            2: 0xFFFF00,
            3: 0xFFA500,
            4: 0xFF0000,
            5: 0xb45428  
        }.get(privilege_value, 0x808080)

        if language_id == 1:
            embed = discord.Embed(title=f"User Information for {username}", color=color)
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name="Username", value=username, inline=True)
            if user_nickname != username:
                embed.add_field(name="Nickname in server", value=user_nickname, inline=True)
            embed.add_field(name="User ID", value=user_id, inline=True)
            embed.add_field(name="Account Created", value=created_at, inline=True)
            embed.add_field(name="Joined Server", value=joined_at, inline=True)
            embed.add_field(name="Server Booster", value=has_nitro, inline=True)
            embed.add_field(name="Badges", value=", ".join(badges) if badges else "No badges", inline=True)
            embed.add_field(name="AbbyBot Privilege", value=privilege_name, inline=True)
            embed.add_field(name="User Birthday", value=user_birthday, inline=True)
            embed.add_field(name="Is active in the AbbyBot project?", value=is_active, inline=True)
            embed.add_field(name="Is Admin?", value=is_admin, inline=True)
            embed.add_field(name="Is Bot?", value=is_bot, inline=True)
            embed.add_field(name="Roles", value=roles, inline=True)

        elif language_id == 2:
            embed = discord.Embed(title=f"Información del Usuario {username}", color=color)
            embed.set_thumbnail(url=avatar_url)
            if user_nickname != username:
                embed.add_field(name="Nombre de usuario", value=username, inline=True)
            embed.add_field(name="Apodo en servidor", value=user_nickname, inline=True)
            embed.add_field(name="ID de usuario", value=user_id, inline=True)
            embed.add_field(name="Cuenta creada", value=created_at, inline=True)
            embed.add_field(name="Se unió al servidor", value=joined_at, inline=True)
            embed.add_field(name="Impulsor del servidor", value="Sí" if has_nitro == "Yes" else "No", inline=True)
            embed.add_field(name="Insignias", value=", ".join(badges) if badges else "Sin insignias", inline=True)
            embed.add_field(name="Privilegio de AbbyBot", value=privilege_name, inline=True)
            embed.add_field(name="Fecha de Cumpleaños", value=user_birthday, inline=True)
            embed.add_field(name="Está activo en el proyecto AbbyBot?", value=is_active, inline=True)
            embed.add_field(name="Es Admin?", value=is_admin, inline=True)
            embed.add_field(name="Es Bot?", value=is_bot, inline=True)
            embed.add_field(name="Roles", value=roles, inline=True)

        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

        embed.set_footer(
            text="AbbyBot",  
            icon_url=bot_avatar_url  
        )

        await interaction.response.send_message(embed=embed)

        cursor.close()
        db.close()



    @app_commands.command(name="banner", description="Get user banner")
    @app_commands.describe(member="The user you want to get their banner.")
    async def user_banner(self, interaction: discord.Interaction, member: discord.Member = None):

        if member is None:
            member = interaction.user

        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        bot_id = 1028065784016142398  # AbbyBot ID
        guild_id = interaction.guild_id

        # Fetching the user's profile to access the banner
        user = await self.bot.fetch_user(member.id)

        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        language_id = result[0]  # The language ID from the query


    # Check if the user executing the command (interaction.user) is active or inactive
        user_id = interaction.user.id  
        cursor.execute("SELECT is_active FROM user_profile WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("User not found in the database.", ephemeral=True)
            cursor.close()
            db.close()
            return
        
        is_active = result[0]

        # If the person executing the command is inactive, send the DM to interaction.user
        if is_active == 0:
            try:
                # Get the embed and file for inactive users
                embed_inactive, file_inactive = await account_inactive_embed(self.bot)

                # Send embed to dm
                await interaction.user.send(embed=embed_inactive, file=file_inactive)
                
                print(f"User {interaction.user} is inactive and notified.")
            except discord.Forbidden:
                print(f"Could not send DM to {interaction.user}. They may have DMs disabled.")
            
            
            cursor.close()
            db.close()

            # Notify user is inactive
            await interaction.response.send_message(
                "Request Rejected: Your account has been listed as **inactive** in the AbbyBot system, please check your DM.",
                ephemeral=True
            )
            return


        if user.banner:
            # If the user has a banner, send the banner URL
            banner_url = user.banner.url
            if language_id == 1:
                embed = discord.Embed(
                    title=f"{member.display_name}'s Banner",
                    color=discord.Color.blue()
                )
                embed.set_image(url=banner_url)
                embed.add_field(name="What a pretty banner, huh?", value='\u200b', inline=True)
            elif language_id == 2:
                embed = discord.Embed(
                    title=f"Banner de {member.display_name}",
                    color=discord.Color.blue()
                )
                embed.set_image(url=banner_url)
                embed.add_field(name="Pero que banner más bonito, huh?", value='\u200b', inline=True)
        else:
            # If the user doesn't have a banner
            if language_id == 1:
                await interaction.response.send_message(f"{member.display_name} does not have a banner. Please try another user.", ephemeral=True)
            elif language_id == 2:
                await interaction.response.send_message(f"{member.display_name} no tiene un banner. Por favor, prueba con otro usuario.", ephemeral=True)
            cursor.close()
            db.close()
            return  # End the command if there's no banner

        # Adding the footer and sending the embed
        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)
        embed.set_footer(text="AbbyBot", icon_url=bot_avatar_url)

        await interaction.response.send_message(embed=embed)

        cursor.close()
        db.close()

    @app_commands.command(name="avatar", description="Get user avatar")
    @app_commands.describe(member="The user you want to get their avatar.")
    async def user_avatar(self, interaction: discord.Interaction, member: discord.Member = None):

        if member is None:
            member = interaction.user  

        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        bot_id = 1028065784016142398  # AbbyBot ID
        guild_id = interaction.guild_id

        # Fetching the user's profile to access the banner
        user = await self.bot.fetch_user(member.id)

        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        language_id = result[0]  # The language ID from the query

        # Check if the user executing the command (interaction.user) is active or inactive
        user_id = interaction.user.id  
        cursor.execute("SELECT is_active FROM user_profile WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("User not found in the database.", ephemeral=True)
            cursor.close()
            db.close()
            return
        
        is_active = result[0]

        # If the person executing the command is inactive, send the DM to interaction.user
        if is_active == 0:
            try:
                # Get the embed and file for inactive users
                embed_inactive, file_inactive = await account_inactive_embed(self.bot)

                # Send embed to dm
                await interaction.user.send(embed=embed_inactive, file=file_inactive)
                
                print(f"User {interaction.user} is inactive and notified.")
            except discord.Forbidden:
                print(f"Could not send DM to {interaction.user}. They may have DMs disabled.")
            
            
            cursor.close()
            db.close()

            # Notify user is inactive
            await interaction.response.send_message(
                "Request Rejected: Your account has been listed as **inactive** in the AbbyBot system, please check your DM.",
                ephemeral=True
            )
            return

        # Then create embed
        if user.avatar:
            avatar_url = user.avatar.url
            if language_id == 1:
                embed = discord.Embed(
                    title=f"{member.display_name}'s Avatar",
                    color=discord.Color.blue()
                )
                embed.set_image(url=avatar_url)
                embed.add_field(name="Look at that awesome avatar!", value='\u200b', inline=True)
            elif language_id == 2:
                embed = discord.Embed(
                    title=f"Avatar de {member.display_name}",
                    color=discord.Color.blue()
                )
                embed.set_image(url=avatar_url)
                embed.add_field(name="¡Miren ese increíble avatar!", value='\u200b', inline=True)
        else:
            if language_id == 1:
                await interaction.response.send_message(f"{member.display_name} does not have an avatar. Please try another user.", ephemeral=True)
            elif language_id == 2:
                await interaction.response.send_message(f"{member.display_name} no tiene un avatar. Por favor, prueba con otro usuario.", ephemeral=True)
            cursor.close()
            db.close()
            return  # If no avatar stop command

        # Footer
        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)
        embed.set_footer(text="AbbyBot", icon_url=bot_avatar_url)

        await interaction.response.send_message(embed=embed)

        cursor.close()
        db.close()

    @app_commands.command(name="decoration", description="Get user avatar decoration")
    @app_commands.describe(member="The user you want to get their avatar decoration.")
    async def user_avatar(self, interaction: discord.Interaction, member: discord.Member = None):

        if member is None:
            member = interaction.user  

        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        bot_id = 1028065784016142398  # AbbyBot ID
        guild_id = interaction.guild_id

        # Fetching the user's profile to access the banner
        user = await self.bot.fetch_user(member.id)

        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        language_id = result[0]  # The language ID from the query

        # Check if the user executing the command (interaction.user) is active or inactive
        user_id = interaction.user.id  
        cursor.execute("SELECT is_active FROM user_profile WHERE user_id = %s;", (user_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("User not found in the database.", ephemeral=True)
            cursor.close()
            db.close()
            return
        
        is_active = result[0]

        # If the person executing the command is inactive, send the DM to interaction.user
        if is_active == 0:
            try:
                # Get the embed and file for inactive users
                embed_inactive, file_inactive = await account_inactive_embed(self.bot)

                # Send embed to dm
                await interaction.user.send(embed=embed_inactive, file=file_inactive)
                
                print(f"User {interaction.user} is inactive and notified.")
            except discord.Forbidden:
                print(f"Could not send DM to {interaction.user}. They may have DMs disabled.")
            
            
            cursor.close()
            db.close()

            # Notify user is inactive
            await interaction.response.send_message(
                "Request Rejected: Your account has been listed as **inactive** in the AbbyBot system, please check your DM.",
                ephemeral=True
            )
            return

        # Then create embed
        if user.avatar_decoration:
            avatar_decoration_url = user.avatar_decoration.url
            if language_id == 1:
                embed = discord.Embed(
                    title=f"{member.display_name}'s Avatar decoration",
                    color=discord.Color.blue()
                )
                embed.set_image(url=avatar_decoration_url)
                embed.add_field(name="Look at that awesome decoration!", value='\u200b', inline=True)
            elif language_id == 2:
                embed = discord.Embed(
                    title=f"Decoración de Avatar de {member.display_name}",
                    color=discord.Color.blue()
                )
                embed.set_image(url=avatar_decoration_url)
                embed.add_field(name="¡Miren esa increíble decoración!", value='\u200b', inline=True)
        else:
            if language_id == 1:
                await interaction.response.send_message(f"{member.display_name} does not have an avatar decoration. Please try another user.", ephemeral=True)
            elif language_id == 2:
                await interaction.response.send_message(f"{member.display_name} no tiene una decoración en su avatar. Por favor, prueba con otro usuario.", ephemeral=True)
            cursor.close()
            db.close()
            return  # If no avatar stop command

        # Footer
        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)
        embed.set_footer(text="AbbyBot", icon_url=bot_avatar_url)

        await interaction.response.send_message(embed=embed)

        cursor.close()
        db.close()
