# Update user status (active/inactive) without overriding previous inactive status
def update_user_status(guild, cursor, db):
    # Get all registered users in the database for this server, now from `user_profile` via a join with `dashboard`
    cursor.execute("""
        SELECT up.user_id, up.is_active 
        FROM user_profile up
        JOIN dashboard d ON up.id = d.user_profile_id 
        WHERE d.guild_id = %s
    """, (guild.id,))
    stored_users = cursor.fetchall()

    # Create a set of current server members' user IDs
    guild_members = {member.id for member in guild.members}

    # Update the status of each user
    for user_id, is_active in stored_users:
        # If the user is already inactive (is_active = 0), do not change its status
        if is_active == 0:
            continue

        # If the user is on the server, mark them as active, otherwise inactive
        new_status = 1 if user_id in guild_members else 0
        cursor.execute("""
            UPDATE user_profile 
            SET is_active = %s 
            WHERE user_id = %s
        """, (new_status, user_id))

    db.commit()