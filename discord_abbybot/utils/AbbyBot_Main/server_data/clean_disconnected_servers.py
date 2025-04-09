def clean_disconnected_servers(cursor, db, active_guild_ids):
    # Get all servers registered in the database
    cursor.execute("SELECT guild_id FROM server_settings")
    registered_guilds = cursor.fetchall()
    
    for (guild_id,) in registered_guilds:
        if guild_id not in active_guild_ids:
            # If the server is not on the servers where the bot is active, we delete the data from the DB
            try:
                # Clear server related logs
                cursor.execute("DELETE FROM mention_counter WHERE user_server = %s", (guild_id,))
                cursor.execute("DELETE FROM user_roles WHERE guild_id = %s", (guild_id,))
                cursor.execute("DELETE FROM dashboard WHERE guild_id = %s", (guild_id,))
                cursor.execute("DELETE FROM server_settings WHERE guild_id = %s", (guild_id,))
                db.commit()
                print(f"\033[32mServer with guild_id {guild_id} has been removed from the database.\033[0m")
            except Exception as e:
                db.rollback()
                print(f"\033[31mError removing server {guild_id}: {e}\033[0m")