from utils.AbbyBot_Main.server_data.register_user_roles import register_user_roles


def register_members(guild, cursor, db):
    for member in guild.members:
        is_bot = 1 if member.bot else 0
        is_admin = 1 if member.guild_permissions.administrator else 0

        # Get user created_at date
        account_created_at = member.created_at

        # Obtain the user's display_name on the server, if they do not have a nickname, use the username
        user_server_nickname = member.display_name if member.display_name else member.name

        # Register or update user in user_profile (global data)
        cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (member.id,))
        user_profile = cursor.fetchone()

        if user_profile is None:
            # Insert new user into user_profile if not exists
            cursor.execute("""
                INSERT INTO user_profile 
                (user_id, user_username, account_created_at, user_privilege) 
                VALUES (%s, %s, %s, 1)
                """, 
                (member.id, member.name, account_created_at)
            )
            db.commit()

            # Retrieve the new user_profile_id
            cursor.execute("SELECT id FROM user_profile WHERE user_id = %s", (member.id,))
            user_profile = cursor.fetchone()

        user_profile_id = user_profile[0]

        # Register or update member data in dashboard (server-specific data)
        cursor.execute("SELECT id FROM dashboard WHERE guild_id = %s AND user_profile_id = %s", (guild.id, user_profile_id))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO dashboard 
                (guild_id, user_profile_id, is_bot, is_admin, user_server_nickname) 
                VALUES (%s, %s, %s, %s, %s)
                """, 
                (guild.id, user_profile_id, is_bot, is_admin, user_server_nickname)
            )
        else:
            cursor.execute("""
                UPDATE dashboard 
                SET is_bot = %s, is_admin = %s, user_server_nickname = %s
                WHERE guild_id = %s AND user_profile_id = %s
                """, 
                (is_bot, is_admin, user_server_nickname, guild.id, user_profile_id)
            )

        db.commit()
        register_user_roles(guild.id, member, cursor, db)