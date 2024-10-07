import discord
from discord.ext import commands, tasks
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

# Load dotenv variables
load_dotenv()

class BirthdayEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        # Connect to the database
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = db.cursor()

        # Get the current date (ensure it's in correct format)
        today = datetime.now().date()
        today_str = today.strftime('%Y-%m-%d')
        print(f"Today's date is: {today_str}")  # Debug print to verify date format

        # Query to find users with a birthday today per server
        cursor.execute("""
            SELECT up.user_id, ds.guild_id, ss.birthday_channel
            FROM user_profile up
            JOIN dashboard ds ON up.id = ds.user_profile_id
            JOIN server_settings ss ON ds.guild_id = ss.guild_id
            WHERE MONTH(up.user_birthday) = %s AND DAY(up.user_birthday) = %s AND up.is_active = 1;
        """, (today.month, today.day))

        birthdays = cursor.fetchall()

        # Loop over each user and server
        for user_id, guild_id, birthday_channel in birthdays:
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                print(f"Guild {guild_id} not found. Skipping.")
                continue

            # Fetch the member from the guild
            member = guild.get_member(user_id)
            if member is None:
                print(f"Member {user_id} not found in guild {guild.name}. Skipping.")
                continue

            # Fetch the correct user_profile_id from the user_profile table
            cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()

            if not result:
                print(f"No user_profile found for {user_id}")
                continue

            user_profile_id = result[0]

            # Query to check if the birthday message was already sent today in this server
            cursor.execute("""
                SELECT last_birthday_announcement 
                FROM dashboard 
                WHERE user_profile_id = %s AND guild_id = %s
            """, (user_profile_id, guild_id))
            last_announcement = cursor.fetchone()

            # Check if the birthday message was already sent today
            if last_announcement and last_announcement[0]:
                last_announcement_date = last_announcement[0].strftime('%Y-%m-%d')
                if last_announcement_date == today_str:
                    print(f"Birthday message already sent for {member} in guild {guild.name} today. Skipping.")
                    continue  # Skip if already sent today

            try:
                # Check if birthday_channel is not NULL and valid
                if birthday_channel:
                    channel = guild.get_channel(birthday_channel)
                    if channel:
                        await channel.send(f"🎉 Happy Birthday, {member.mention}! 🎂 AbbyBot and everyone wish you a wonderful day! 🎉")
                        print(f"Sent birthday message to {member} in guild {guild.name}")
                    else:
                        print(f"Channel {birthday_channel} not found in guild {guild.name}. Skipping.")
                        continue
                else:
                    print(f"No birthday channel set for guild {guild.name}. Skipping.")
                    continue

                # Debugging: Print the exact SQL query before executing
                print(f"Executing SQL: UPDATE dashboard SET last_birthday_announcement = '{today_str}' WHERE user_profile_id = {user_profile_id} AND guild_id = {guild_id}")

                # Update last_birthday_announcement to today's date
                cursor.execute("""
                    UPDATE dashboard 
                    SET last_birthday_announcement = %s 
                    WHERE user_profile_id = %s AND guild_id = %s
                """, (today_str, user_profile_id, guild_id))
                
                # Debugging: Check affected rows
                if cursor.rowcount == 0:
                    print(f"Update failed for user_profile_id {user_profile_id} in guild {guild_id}")
                else:
                    print(f"Update successful for user_profile_id {user_profile_id} in guild {guild_id}")

                db.commit()  # Commit the transaction to save changes

            except discord.Forbidden:
                print(f"Could not send birthday message to {member} in guild {guild.name}. Missing permissions.")

        # Close the database connection
        cursor.close()
        db.close()

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        print("Waiting for bot to be ready...")
        await self.bot.wait_until_ready()

