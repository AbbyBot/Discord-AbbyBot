import discord
from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

class ChannelUpdateEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event: on_guild_channel_update
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        # Load dotenv variables
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        guild_id = before.guild.id

        # Check if the server has activated_logs = 1
        cursor.execute("SELECT activated_logs FROM server_settings WHERE guild_id = %s", (guild_id,))
        logs_result = cursor.fetchone()

        if logs_result is None or logs_result[0] == 0:
            # If it is not activated or there is no result, do nothing
            cursor.close()
            db.close()
            return

        # Check server language
        cursor.execute("SELECT guild_language FROM server_settings WHERE guild_id = %s", (guild_id,))
        result = cursor.fetchone()

        if result is None:
            # If the server is not registered, do nothing
            cursor.close()
            db.close()
            return

        changes = []

        # Compare relevant attributes between 'before' and 'after'
        if before.name != after.name:
            changes.append(f"Channel name changed from **{before.name}** to **{after.name}**.")

        if before.category != after.category:
            before_category = before.category.name if before.category else "No category"
            after_category = after.category.name if after.category else "No category"
            changes.append(f"Category changed from **{before_category}** to **{after_category}**.")

        # Only check for slowmode_delay if it's a TextChannel
        if isinstance(before, discord.TextChannel) and isinstance(after, discord.TextChannel):
            if before.slowmode_delay != after.slowmode_delay:
                changes.append(f"Slowmode delay changed from **{before.slowmode_delay}**s to **{after.slowmode_delay}**s.")

        # Only check for topic if it's a TextChannel
        if isinstance(before, discord.TextChannel) and isinstance(after, discord.TextChannel):
            if (before.topic or "No topic") != (after.topic or "No topic"):  # Ensure empty topics are treated as 'No topic'
                before_topic = before.topic if before.topic else "No topic"
                after_topic = after.topic if after.topic else "No topic"
                changes.append(f"Channel topic changed from **{before_topic}** to **{after_topic}**.")

        # If there are no changes, exit the function
        if not changes:
            cursor.close()
            db.close()
            return

        # Check language and create response message
        language_id = result[0]
        if language_id == 1:
            response_message = f"Updates to channel **{before.name}**:\n" + "\n".join(changes)
        elif language_id == 2:
            response_message = f"Actualizaciones en el canal **{before.name}**:\n" + "\n".join(changes)

        # Get logs_channel ID
        cursor.execute("SELECT logs_channel FROM server_settings WHERE guild_id = %s", (guild_id,))
        default_channel = cursor.fetchone()

        if default_channel is not None and default_channel[0] is not None:
            logs_channel = self.bot.get_channel(default_channel[0])  # Get the TextChannel object

            if logs_channel is not None:
                await logs_channel.send(response_message)

        # Close db
        cursor.close()
        db.close()
