import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class RoleUpdateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event: on_guild_role_update
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        guild_id = after.guild.id

        # Check if logs are activated
        cursor.execute("SELECT activated_logs FROM server_settings WHERE guild_id = %s", (guild_id,))
        logs_result = cursor.fetchone()

        if logs_result is None or logs_result[0] == 0:
            # If the logs are not activated or there is no result, do nothing
            cursor.close()
            db.close()
            return

        # Check guild language
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            # If the server is not registered, do nothing
            cursor.close()
            db.close()
            return

        language_id = result[0]

        # Compare role attributes and generate changes
        changes = []

        if before.name != after.name:
            changes.append(f"Name changed from **{before.name}** to **{after.name}**." if language_id == 1 else f"Nombre cambiado de **{before.name}** a **{after.name}**.")
        
        if before.permissions != after.permissions:
            changes.append(f"Permissions updated.")
        
        if before.color != after.color:
            changes.append(f"Color changed from **{before.color}** to **{after.color}**." if language_id == 1 else f"Color cambiado de **{before.color}** a **{after.color}**.")
        
        if before.position != after.position:
            changes.append(f"Position changed from **{before.position}** to **{after.position}**." if language_id == 1 else f"Posición cambiada de **{before.position}** a **{after.position}**.")
        
        # If there are changes, create a message for the logs
        if changes:
            changes_message = "\n".join(changes)
            response_message = (f"The role **{before.name}** has been updated:\n{changes_message}" 
                                if language_id == 1 else 
                                f"El rol **{before.name}** ha sido actualizado:\n{changes_message}")
            
            # Get logs channel ID
            cursor.execute("SELECT logs_channel FROM server_settings WHERE guild_id = %s", (guild_id,))
            default_channel = cursor.fetchone()

            if default_channel is not None and default_channel[0] is not None:
                logs_channel = self.bot.get_channel(default_channel[0])  # Get the TextChannel object

                if logs_channel is not None:
                    # Send the role update to the logs channel
                    await logs_channel.send(response_message)

        # Event: on_member_update - handle when roles are added/removed from a user
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        guild_id = after.guild.id

        # Check if logs are activated
        cursor.execute("SELECT activated_logs FROM server_settings WHERE guild_id = %s", (guild_id,))
        logs_result = cursor.fetchone()

        if logs_result is None or logs_result[0] == 0:
            # If logs are not activated or no result, do nothing
            cursor.close()
            db.close()
            return

        # Check guild language
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            # If the server is not registered, do nothing
            cursor.close()
            db.close()
            return

        language_id = result[0]

        # Compare roles before and after the change
        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added_roles = after_roles - before_roles  # Roles that were added
        removed_roles = before_roles - after_roles  # Roles that were removed

        changes = []

        # Process added roles
        for role in added_roles:
            changes.append(
                f"**{before.display_name}** was given the role **{role.name}**." if language_id == 1 
                else f"A **{before.display_name}** se le ha otorgado el rol **{role.name}**."
            )

        # Process removed roles
        for role in removed_roles:
            changes.append(
                f"**{before.display_name}** had the role **{role.name}** removed." if language_id == 1 
                else f"Se ha eliminado el rol **{role.name}** de **{before.display_name}**."
            )

        # If there are changes, create a message for the logs
        if changes:
            changes_message = "\n".join(changes)
            response_message = (f"Role changes for **{before.display_name}**:\n{changes_message}"
                                if language_id == 1 else
                                f"Cambios de rol para **{before.display_name}**:\n{changes_message}")

            # Get logs channel ID
            cursor.execute("SELECT logs_channel FROM server_settings WHERE guild_id = %s", (guild_id,))
            default_channel = cursor.fetchone()

            if default_channel is not None and default_channel[0] is not None:
                logs_channel = self.bot.get_channel(default_channel[0])  # Get the TextChannel object

                if logs_channel is not None:
                    # Send the role changes to the logs channel
                    await logs_channel.send(response_message)

        # Close db connection
        cursor.close()
        db.close()
