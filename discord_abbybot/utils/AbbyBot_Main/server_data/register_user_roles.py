# Register or update user roles
def register_user_roles(guild_id, member, cursor, db):
    cursor.execute("DELETE FROM user_roles WHERE guild_id = %s AND user_profile_id = (SELECT id FROM user_profile WHERE user_id = %s)", (guild_id, member.id))
    db.commit()

    for role in member.roles:
        if not role.is_default():
            cursor.execute("""
                INSERT INTO user_roles (guild_id, user_profile_id, role_id, role_name) 
                VALUES (%s, (SELECT id FROM user_profile WHERE user_id = %s), %s, %s)
                """, 
                (guild_id, member.id, role.id, role.name)
            )
            db.commit()