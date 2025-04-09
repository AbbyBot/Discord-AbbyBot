# Function to register or update server channels
def register_channels(guild, cursor, db):
    for channel in guild.channels:
        cursor.execute("SELECT id FROM server_channels WHERE guild_id = %s AND channel_id = %s", (guild.id, channel.id))
        result = cursor.fetchone()

        if result is None:
            # Insert new channel
            cursor.execute("""
                INSERT INTO server_channels (guild_id, channel_id, channel_title) 
                VALUES (%s, %s, %s)
            """, (guild.id, channel.id, channel.name))
            print(f"\033[32mChannel {channel.name} added to server {guild.name}.\033[0m")
        else:
            # Update existing channel
            cursor.execute("""
                UPDATE server_channels 
                SET channel_title = %s 
                WHERE guild_id = %s AND channel_id = %s
            """, (channel.name, guild.id, channel.id))
            print(f"\033[33mChannel {channel.name} updated in server {guild.name}.\033[0m")

    db.commit()