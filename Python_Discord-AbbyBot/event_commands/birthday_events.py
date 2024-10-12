import discord
from discord.ext import commands, tasks
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from utils.utils import get_bot_avatar

bot_id = 1028065784016142398  # AbbyBot ID

# Load dotenv variables
load_dotenv()

class BirthdayEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()

    @tasks.loop(minutes=20)
    async def check_birthdays(self):
        print("\033[36m" + "Starting birthday verification..." + "\033[0m")

        # Get UTC date
        today = datetime.now(timezone.utc).date()
        today_str = today.strftime('%Y-%m-%d')
        print(f"\033[36mCurrent date: {today_str}\033[0m")

        # DB settings
        try:
            db = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            cursor = db.cursor()
        except mysql.connector.Error:
            return

        # SQL query to find users with birthdays today
        try:
            cursor.execute("""
                SELECT up.user_id, ds.guild_id, ss.birthday_channel, ss.guild_language, up.user_birthday
                FROM user_profile up
                JOIN dashboard ds ON up.id = ds.user_profile_id
                JOIN server_settings ss ON ds.guild_id = ss.guild_id
                WHERE MONTH(up.user_birthday) = %s AND DAY(up.user_birthday) = %s AND up.is_active = 1;
            """, (today.month, today.day))
            birthdays = cursor.fetchall()
        except mysql.connector.Error:
            cursor.close()
            db.close()
            return

        # Iterate over users and servers with birthdays today
        for user_id, guild_id, birthday_channel, guild_language, user_birthday in birthdays:
            print(f"\033[36mProcessing user {user_id} in the guild {guild_id}\033[0m")
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                print(f"\033[31mGuild {guild_id} not found. Skipping.\033[0m")
                continue

            member = guild.get_member(user_id)
            if member is None:
                print(f"\033[31mMember {user_id} not found in guild {guild.name}. Skipping.\033[0m")
                continue

            # Get user_profile_id
            cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (user_id,))
            user_profile = cursor.fetchone()

            if not user_profile:
                print(f"\033[31mUser profile not found for user_id {user_id}\033[0m")
                continue

            user_profile_id = user_profile[0]
            print(f"\033[32mFound user_profile_id: {user_profile_id} for user_id: {user_id}\033[0m")

            # Calculate user age
            birth_date = user_birthday
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            # Check if the birthday message for this user has already been sent today
            cursor.execute("""
                SELECT last_birthday_announcement 
                FROM dashboard 
                WHERE user_profile_id = %s AND guild_id = %s
            """, (user_profile_id, guild_id))
            last_announcement = cursor.fetchone()

            if last_announcement and last_announcement[0]:
                last_announcement_date = last_announcement[0].strftime('%Y-%m-%d')
                if last_announcement_date == today_str:
                    print(f"\033[33mThe birthday message was already sent today for {member} in the guild {guild.name}. Omitting.\033[0m")
                    continue

            try:
                # Check if the birthday channel is valid
                if birthday_channel:
                    channel = guild.get_channel(birthday_channel)
                    if channel:
                        # Create the birthday embed
                        embed = discord.Embed(
                            title=f"🎉 Happy {age}th Birthday!" if guild_language == 1 else f"🎉 ¡Felices {age} años!",
                            description=f"🎂 {member.mention}, AbbyBot and everyone wish you a wonderful day!" if guild_language == 1 else f"🎂 {member.mention}, AbbyBot y todos te deseamos un día maravilloso.",
                            color=discord.Color.gold()
                        )
                        embed.set_thumbnail(url=member.avatar.url)
                        bot_avatar_url = await get_bot_avatar(self.bot, bot_id)

                        embed.set_footer(text="AbbyBot, Happy birthday! 🎉" if guild_language == 1 else "AbbyBot, ¡Feliz cumpleaños! 🎉", icon_url=bot_avatar_url)

                        # Send birthday message
                        await channel.send(embed=embed)
                        print(f"\033[32mBirthday message sent to {member} in the guild {guild.name}\033[0m")
                    else:
                        print(f"\033[31mChannel {birthday_channel} not found in guild {guild.name}. Omitting.\033[0m")
                        continue
                else:
                    print(f"\033[31mA birthday channel has not been configured for the guild {guild.name}. Omitting.\033[0m")
                    continue

                # Update latest birthday announcement
                cursor.execute("""
                    UPDATE dashboard 
                    SET last_birthday_announcement = %s 
                    WHERE user_profile_id = %s AND guild_id = %s
                """, (today_str, user_profile_id, guild_id))

                db.commit()
                if cursor.rowcount == 0:
                    print(f"\033[33mNo rows updated for user_profile_id {user_profile_id} in guild {guild_id}\033[0m")
                else:
                    print(f"\033[32mSuccessful update for user_profile_id {user_profile_id} in guild {guild_id}\033[0m")

            except discord.Forbidden:
                print(f"\033[31mCould not send birthday message to {member} in guild {guild.name}. Permissions are missing.\033[0m")

        cursor.close()
        db.close()

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        print("\033[36mWaiting for the bot to be ready...\033[0m")
        await self.bot.wait_until_ready()
        print("\033[36mThe bot is now ready. Starting birthday verification.\033[0m")
