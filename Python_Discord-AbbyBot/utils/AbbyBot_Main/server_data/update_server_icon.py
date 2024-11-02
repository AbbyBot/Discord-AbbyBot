import random
from datetime import datetime

# Function to update the server icon if it has changed
def update_server_icon(guild, cursor, db):
    # Get the URL of the server icon or a default URL if it has no icon
    random_avatar = random.randint(1, 5)
    guild_icon_url = str(guild.icon.url) if guild.icon else f'https://cdn.discordapp.com/embed/avatars/{random_avatar}.png'

    # Get the URL stored in the database
    cursor.execute("SELECT guild_icon_url FROM server_settings WHERE guild_id = %s", (guild.id,))
    result = cursor.fetchone()
    stored_icon_url = result[0] if result else None

    # Compare the stored URL with the new icon URL
    if stored_icon_url == guild_icon_url:
        print("\033[34m" + "Icon has not changed for " + guild.name + ", skipping update." + "\033[0m")
        return

    # Update the icon URL in the database if it has changed
    cursor.execute("""
        UPDATE server_settings 
        SET guild_icon_url = %s, guild_icon_last_updated = %s
        WHERE guild_id = %s
        """, 
        (guild_icon_url, datetime.now(), guild.id)
    )
    db.commit()