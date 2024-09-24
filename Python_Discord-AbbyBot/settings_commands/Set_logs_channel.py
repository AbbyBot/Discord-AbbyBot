import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
from dotenv import load_dotenv
import os
from embeds.embeds import account_inactive_embed # import embed system

# Load dotenv variables
load_dotenv()

class SetLogsChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_logs_channel", description="Assign a channel for AbbyBot to send logs of all server actions.")
    async def command_name(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Connect to the database using environment variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get guild_id and user_id from the interaction
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        # Check if the user is active (is_active = 1) or inactive (is_active = 0)
        cursor.execute("SELECT is_active FROM dashboard WHERE guild_id = %s AND user_id = %s", (guild_id, user_id))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("User not found in the database.", ephemeral=True)
            cursor.close()
            db.close()
            return

        # If the user is inactive (banned), send an embed in DM and exit
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
            
            cursor.close()
            db.close()
            await interaction.response.send_message("Request Rejected: Your account has been listed as **inactive** in the AbbyBot system, please check your DM.", ephemeral=True)
            return

        # Query to check the server's language setting (obligatory field)
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        current_language_id = cursor.fetchone()[0]

        if current_language_id is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return
        
        # Check if user has admin permission
        if not interaction.user.guild_permissions.administrator:
            if current_language_id == 1:
                await interaction.response.send_message("You do not have permission to change AbbyBot's logs channel.", ephemeral=True)
                return
            if current_language_id == 2:
                await interaction.response.send_message("No tienes permiso para cambiar el canal de logs de AbbyBot.", ephemeral=True)
                return

        #update channel in database
        cursor.execute("update server_settings set logs_channel = %s where guild_id = %s;", (channel.id, guild_id))
        db.commit()

        # Close the database connection
        cursor.close()
        db.close()


        # Confirm to user
        if current_language_id == 1:
            await interaction.response.send_message(f"Logs channel has been set to {channel.mention}. AbbyBot will send her logs on that channel.", ephemeral=True)
        elif current_language_id == 2:
            await interaction.response.send_message(f"El canal de cumpleaños se ha configurado en {channel.mention}. AbbyBot enviará sus registros en ese canal.", ephemeral=True)

