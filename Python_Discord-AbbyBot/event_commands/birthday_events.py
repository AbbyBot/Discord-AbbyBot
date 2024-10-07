import discord
from discord.ext import commands, tasks
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime
from utils.utils import get_bot_avatar

bot_id = 1028065784016142398  # AbbyBot ID

# Load dotenv variables
load_dotenv()

class BirthdayButtonsView(discord.ui.View):
    def __init__(self, message):
        super().__init__(timeout=None)  # No timeouts for the buttons
        self.message = message

    @discord.ui.button(label="🎉", style=discord.ButtonStyle.primary, emoji="🎉")
    async def celebrate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.message.add_reaction("🎉")

    @discord.ui.button(label="🎂", style=discord.ButtonStyle.success, emoji="🎂")
    async def cake_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.message.add_reaction("🎂")

    @discord.ui.button(label="🎁", style=discord.ButtonStyle.secondary, emoji="🎁")
    async def gift_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.message.add_reaction("🎁")


class BirthdayEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        # Conectar a la base de datos
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get current date
        today = datetime.now().date()
        today_str = today.strftime('%Y-%m-%d')
        print(f"Today's date is: {today_str}")  

        # Query to find users with birthdays today
        cursor.execute("""
            SELECT up.user_id, ds.guild_id, ss.birthday_channel, ss.guild_language, up.user_birthday
            FROM user_profile up
            JOIN dashboard ds ON up.id = ds.user_profile_id
            JOIN server_settings ss ON ds.guild_id = ss.guild_id
            WHERE MONTH(up.user_birthday) = %s AND DAY(up.user_birthday) = %s AND up.is_active = 1;
        """, (today.month, today.day))

        birthdays = cursor.fetchall()

        # Iterate over each user and server
        for user_id, guild_id, birthday_channel, guild_language, user_birthday in birthdays:
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                print(f"Guild {guild_id} not found. Skipping.")
                continue

            # Get the guild member
            member = guild.get_member(user_id)
            if member is None:
                print(f"Member {user_id} not found in guild {guild.name}. Skipping.")
                continue

            # Get the user_profile_id instead of using user_id directly
            cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (user_id,))
            user_profile = cursor.fetchone()

            if not user_profile:
                print(f"No user_profile found for user_id {user_id}")
                continue

            user_profile_id = user_profile[0]  # The correct value of user_profile_id
            print(f"Found user_profile_id: {user_profile_id} for user_id: {user_id}")

            # Calculate age
            birth_date = user_birthday
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            # Check if the message has already been sent today on this server
            cursor.execute("""
                SELECT last_birthday_announcement 
                FROM dashboard 
                WHERE user_profile_id = %s AND guild_id = %s
            """, (user_profile_id, guild_id))
            last_announcement = cursor.fetchone()

            # If the message has already been sent today, avoid duplicates
            if last_announcement and last_announcement[0]:
                last_announcement_date = last_announcement[0].strftime('%Y-%m-%d')
                if last_announcement_date == today_str:
                    print(f"Birthday message already sent for {member} in guild {guild.name} today. Skipping.")
                    continue  # Skip if message has already been sent today

            try:
                # Check if the birthday channel is valid
                if birthday_channel:
                    channel = guild.get_channel(birthday_channel)
                    if channel:
                        # Create the birthday embed
                        embed = discord.Embed(
                            title=f"🎉 ¡Felices {age} años!" if guild_language == 2 else f"🎉 Happy {age}th Birthday!",
                            description=f"🎂 {member.mention}, AbbyBot y todos te deseamos un día maravilloso." if guild_language == 2 else f"🎂 {member.mention}, AbbyBot and everyone wish you a wonderful day!",
                            color=discord.Color.gold()
                        )
                        embed.set_thumbnail(url=member.avatar.url)
                        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)
        
                        embed.set_footer(text="AbbyBot, Happy birthday! 🎉" if guild_language == 1 else "AbbyBot, ¡Feliz cumpleaños! 🎉", icon_url=bot_avatar_url)

                        # Send message
                        birthday_message = await channel.send(embed=embed)
                        print(f"Sent birthday message to {member} in guild {guild.name}")

                        # Add buttons
                        view = BirthdayButtonsView(birthday_message)
                        await channel.send("¡Reacciona al mensaje de cumpleaños con estos botones!" if guild_language == 2 else "React to the birthday message with these buttons!", view=view)

                    else:
                        print(f"Channel {birthday_channel} not found in guild {guild.name}. Skipping.")
                        continue
                else:
                    print(f"No birthday channel set for guild {guild.name}. Skipping.")
                    continue

                # Update latest birthday announcement
                cursor.execute("""
                    UPDATE dashboard 
                    SET last_birthday_announcement = %s 
                    WHERE user_profile_id = %s AND guild_id = %s
                """, (today_str, user_profile_id, guild_id))

                # Confirm that the commit was made
                db.commit()
                if cursor.rowcount == 0:
                    print(f"No rows updated for user_profile_id {user_profile_id} in guild {guild_id}")
                else:
                    print(f"Update successful for user_profile_id {user_profile_id} in guild {guild_id}")

            except discord.Forbidden:
                print(f"Could not send birthday message to {member} in guild {guild.name}. Missing permissions.")

        # Close connection to the database
        cursor.close()
        db.close()

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        print("Waiting for bot to be ready...")
        await self.bot.wait_until_ready()
