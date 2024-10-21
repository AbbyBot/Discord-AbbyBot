import discord
from discord import app_commands
from discord.ext import commands
import os
import mysql.connector
from dotenv import load_dotenv
from embeds.embeds import account_inactive_embed
from utils.utils import get_bot_avatar
import asyncio

# Load dotenv variables
load_dotenv()

# Temporary mp3 folder
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Dictionary to manage playback queues per server
queues = {}  # store (song, user who uploaded it)
current_song_info = {}  # To store the current song and who uploaded it per server

# Define limits
NORMAL_USER_SIZE_LIMIT_MB = 5  # Max file size for normal users in MB
PREMIUM_USER_SIZE_LIMIT_MB = 40  # Max file size for premium users in MB
NORMAL_USER_DURATION_LIMIT = 120  # Max duration for normal users in seconds (2 minutes)
PREMIUM_USER_DURATION_LIMIT = 600  # Max duration for premium users in seconds (10 minutes)

class MusicPlayer(commands.GroupCog, name="music"):
    def __init__(self, bot):
        self.bot = bot

    # Normal user music play command
    @app_commands.command(name="play", description="Play an mp3 audio (normal users).")
    async def music_play(self, interaction: discord.Interaction, file: discord.Attachment):
        await self._play_music(interaction, file, is_premium=False)
    
    # Premium user music play command
    @app_commands.command(name="premium", description="Play an mp3 audio (premium users).")
    async def music_premium(self, interaction: discord.Interaction, file: discord.Attachment):
        await self._play_music(interaction, file, is_premium=True)

    # Skip command to skip the current song
    @app_commands.command(name="skip", description="Skip the current song.")
    async def skip_song(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id

        # Connect to the database
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get the language ID for the server
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=False)
            cursor.close()
            db.close()
            return

        language_id = result[0]  # The language ID from the query



        # Check if there is a song currently playing
        if guild_id not in current_song_info or current_song_info[guild_id] is None:
            await interaction.response.send_message("There is no song to skip." if language_id == 1 else "No hay ninguna canción que saltar.", ephemeral=False)
        else:
            voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            if voice_client and voice_client.is_playing():
                voice_client.stop()  # Stop the current song to trigger playing the next one
                await interaction.response.send_message("Song skipped!" if language_id == 1 else "¡Canción saltada!", ephemeral=False)

    # Command to view the current queue
    @app_commands.command(name="queue", description="View the current song queue.")
    async def view_queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id

        # Connect to the database
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get the language ID for the server
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        language_id = result[0]  # The language ID from the query

        bot_id = 1028065784016142398  # AbbyBot ID

        # If there is no queue for this server
        if guild_id not in queues or len(queues[guild_id]) == 0:
            embed = discord.Embed(
                title="🎵 Queue" if language_id == 1 else "🎵 Cola de Reproducción",
                description="The queue is empty. Use `/music play` to add songs." if language_id == 1 else 
                "La cola está vacía. Usa `/music play` para añadir canciones.",
                color=discord.Color.red()
            )

            bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

            embed.set_footer(
                text="AbbyBot",  
                icon_url=bot_avatar_url  
            )

            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            # Show the list of songs in the queue
            queue_list = queues[guild_id]
            embed = discord.Embed(
                title="🎵 Queue" if language_id == 1 else "🎵 Cola de Reproducción",
                description=f"There are currently {len(queue_list)} song(s) in the queue." if language_id == 1 else 
                f"Actualmente hay {len(queue_list)} canción(es) en la cola.",
                color=discord.Color.green()
            )

            bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

            embed.set_footer(
                text="AbbyBot",  
                icon_url=bot_avatar_url  
            )

            # List the songs
            for idx, (song, user) in enumerate(queue_list, start=1):
                filename = os.path.basename(song)  # Show only the file name
                embed.add_field(
                    name=f"Song {idx}" if language_id == 1 else f"Canción {idx}", 
                    value=f"{filename} (uploaded by {user.display_name})" if language_id == 1 else 
                    f"{filename} (subido por {user.display_name})", 
                    inline=False
                )

            await interaction.response.send_message(embed=embed, ephemeral=False)

    # Command to view the current song being played
    @app_commands.command(name="status", description="View the current song being played.")
    async def view_status(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id

        # Connect to the database
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get the language ID for the server
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            await interaction.response.send_message("This server is not registered. Please contact the admin.", ephemeral=True)
            cursor.close()
            db.close()
            return

        language_id = result[0]  # The language ID from the query
    
        bot_id = 1028065784016142398  # AbbyBot ID

        # Check if there is a song currently playing
        if guild_id not in current_song_info or current_song_info[guild_id] is None:
            embed = discord.Embed(
                title="🎵 Now Playing" if language_id == 1 else "🎵 Estado Actual",
                description="There is no song playing right now." if language_id == 1 else 
                "No hay ninguna canción reproduciéndose en este momento.",
                color=discord.Color.red()
            )

            bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

            embed.set_footer(
                text="AbbyBot",  
                icon_url=bot_avatar_url  
            )

            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            song, user = current_song_info[guild_id]  # Get the current song info
            filename = os.path.basename(song)  # Just the file name

            embed = discord.Embed(
                title="🎵 Now Playing" if language_id == 1 else "🎵 Estado Actual",
                description="A song is currently playing." if language_id == 1 else 
                "Actualmente se está reproduciendo una canción.",
                color=discord.Color.blue()
            )

            bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

            embed.set_footer(
                text="AbbyBot",  
                icon_url=bot_avatar_url  
            )
    
            embed.add_field(name="Song" if language_id == 1 else "Canción", value=filename, inline=False)
            embed.add_field(name="Uploaded by" if language_id == 1 else "Subido por", value=user.display_name, inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=False)

    # Shared method to handle music playing
    async def _play_music(self, interaction: discord.Interaction, file: discord.Attachment, is_premium: bool):
        guild_id = interaction.guild.id  # Guild ID

        # Connect to the database
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get the language ID for the server
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
                "Request Rejected: Your account has been listed as **inactive** in the AbbyBot system, please check your DM." if language_id == 1 else 
                "Solicitud rechazada: Tu cuenta ha sido listada como **inactiva** en el sistema AbbyBot, por favor revisa tu DM.",
                ephemeral=False
            )
            return

        # Make sure the user is on a voice channel
        if interaction.user.voice is None:
            await interaction.response.send_message(
                "You must be on a voice channel to use this command." if language_id == 1 else 
                "Debes estar en un canal de voz para usar este comando.", 
                ephemeral=False
            )
            return

        # Check file size (based on user type)
        file_size_mb = file.size / (1024 * 1024)  # Convert file size to MB
        if is_premium:
            if file_size_mb > PREMIUM_USER_SIZE_LIMIT_MB:
                await interaction.response.send_message(
                    f"The file is too large. Premium users can only upload files up to {PREMIUM_USER_SIZE_LIMIT_MB} MB." if language_id == 1 else 
                    f"El archivo es demasiado grande. Los usuarios premium solo pueden subir archivos de hasta {PREMIUM_USER_SIZE_LIMIT_MB} MB.", 
                    ephemeral=False
                )
                return
        else:
            if file_size_mb > NORMAL_USER_SIZE_LIMIT_MB:
                await interaction.response.send_message(
                    f"The file is too large. Normal users can only upload files up to {NORMAL_USER_SIZE_LIMIT_MB} MB." if language_id == 1 else 
                    f"El archivo es demasiado grande. Los usuarios normales solo pueden subir archivos de hasta {NORMAL_USER_SIZE_LIMIT_MB} MB.", 
                    ephemeral=False
                )
                return

        # Create a subfolder for the guild
        guild_folder = os.path.join(UPLOAD_FOLDER, str(guild_id))
        if not os.path.exists(guild_folder):
            os.makedirs(guild_folder)

        # Save the file in the guild-specific folder
        file_path = os.path.join(guild_folder, file.filename)
        await file.save(file_path)

        # Add the song to the server queue with the user who uploaded it
        if guild_id not in queues:
            queues[guild_id] = []
        
        queues[guild_id].append((file_path, interaction.user))  # Add the song and the user to the queue

        # Check if the bot is already in a voice channel on this server
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_client and voice_client.is_connected():
            # If already connected, just add the song to the queue and send a message
            await interaction.response.send_message(
                f"{file.filename} has been added to the queue." if language_id == 1 else 
                f"Se ha añadido {file.filename} a la cola.", 
                ephemeral=False
            )
        else:
            # Connect to the voice channel and start playback
            voice_channel = interaction.user.voice.channel
            voice_client = await voice_channel.connect()

            await interaction.response.send_message(
                f"Playing {file.filename} and connecting to channel {voice_channel}..." if language_id == 1 else 
                f"Reproduciendo {file.filename} y conectando al canal {voice_channel}...", 
                ephemeral=False
            )
            await self.play_next_song(voice_client, guild_id)
    
    async def play_next_song(self, voice_client, guild_id):
        if len(queues[guild_id]) > 0:
            song, user = queues[guild_id].pop(0)  # Take the first song and the user in the queue
            current_song_info[guild_id] = (song, user)  # Store the information of the current song
            voice_client.play(discord.FFmpegPCMAudio(song), after=lambda e: self.bot.loop.create_task(self.on_song_end(voice_client, guild_id, song)))

            # Wait for the song to finish playing
            while voice_client.is_playing():
                await asyncio.sleep(1)
        else:
            # If there are no more songs, disconnect the bot
            current_song_info[guild_id] = None  # No song
            await voice_client.disconnect()

    async def on_song_end(self, voice_client, guild_id, song):
        # Delete the file of the played song
        if os.path.exists(song):
            os.remove(song)

        # Play the next song in the queue
        if len(queues[guild_id]) > 0:
            await self.play_next_song(voice_client, guild_id)
        else:
            # If there are no songs left in the queue, disconnect
            current_song_info[guild_id] = None
            await voice_client.disconnect()

