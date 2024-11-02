import random
from datetime import datetime

from utils.AbbyBot_Main.server_data.register_members import register_members

# Function to register or update a server

def register_server(guild, cursor, db):
    # Default language (English)
    default_language_id = 1
    
    cursor.execute("SELECT guild_id, guild_icon_url FROM server_settings WHERE guild_id = %s", (guild.id,))
    result = cursor.fetchone()

    # Get the Discord icon URL, and use a default URL if there is no icon
    random_avatar = random.randint(1, 5)
    guild_icon_url = str(guild.icon.url) if guild.icon else f'https://cdn.discordapp.com/embed/avatars/{random_avatar}.png'
    
    if result is None:
        # Register the server for the first time
        cursor.execute("""
            INSERT INTO server_settings 
            (guild_id, guild_name, owner_id, member_count, prefix, guild_language, guild_icon_url, guild_icon_last_updated) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            (guild.id, guild.name, guild.owner.id, guild.member_count, 'abbybot_', default_language_id, guild_icon_url, datetime.now())
        )
        print("\033[32m" + f"Server {guild.name} registered." + "\033[0m")
    else:
        # If the server is already registered, update only if the icon URL has changed
        stored_icon_url = result[1]  # URL in bd
        if guild_icon_url != stored_icon_url:
            cursor.execute("""
                UPDATE server_settings 
                SET guild_name = %s, owner_id = %s, member_count = %s, guild_icon_url = %s, guild_icon_last_updated = %s
                WHERE guild_id = %s
                """, 
                (guild.name, guild.owner.id, guild.member_count, guild_icon_url, datetime.now(), guild.id)
            )
            print("\033[33m" + f"Server {guild.name} updated." + "\033[0m") 
    
    db.commit()
    # Register or update server members
    register_members(guild, cursor, db)