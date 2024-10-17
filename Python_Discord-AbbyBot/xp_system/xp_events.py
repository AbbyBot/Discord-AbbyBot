import mysql.connector
from datetime import datetime

def add_xp(user_id, base_xp, reason, cursor, db):
    try:
        # Get the user's privilege multiplier and level
        cursor.execute("""
            SELECT p.xp_multiplier, u.level 
            FROM user_profile u
            JOIN privileges p ON u.user_privilege = p.id
            WHERE u.user_id = %s
        """, (user_id,))
        result = cursor.fetchone()

        if result:
            privilege_multiplier, current_level = result
        else:
            privilege_multiplier = 1.0  # Default multiplier if you don't have privilege
            current_level = 1  # Default level

        # Get the level multiplier
        cursor.execute("SELECT xp_bonus FROM user_levels WHERE level = %s", (current_level,))
        level_multiplier_result = cursor.fetchone()

        level_multiplier = level_multiplier_result[0] if level_multiplier_result else 1.0

        # Calculate the final XP by applying both multipliers
        final_xp = int(base_xp * level_multiplier * privilege_multiplier)

        # We update the user's total XP
        cursor.execute("""
            UPDATE user_profile 
            SET xp_total = xp_total + %s 
            WHERE user_id = %s
        """, (final_xp, user_id))

        # Record the change in xp_history
        cursor.execute("""
            INSERT INTO xp_history (user_id, xp_change, change_reason, change_timestamp) 
            VALUES (%s, %s, %s, %s)
        """, (user_id, final_xp, reason, datetime.now()))

        db.commit()

        print(f"XP added: {final_xp} XP to user {user_id}. Reason: {reason}. (Multiplier: {level_multiplier} x {privilege_multiplier})")

        # Check if the user has leveled up
        check_level_up(user_id, cursor, db)

    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error adding XP: {err}")

# Function to check XP of a user
def check_xp(user_id, cursor):
    cursor.execute("SELECT xp_total FROM user_profile WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    
    if result:
        xp_total = result[0]
        print(f"\033[34mUser {user_id} has {xp_total} XP.\033[0m")
        return xp_total
    else:
        print(f"\033[31mUser {user_id} not found.\033[0m")
        return None

# Function to remove XP from a user (for penalties)
def remove_xp(user_id, xp_amount, reason, cursor, db):
    try:
        cursor.execute("""
            UPDATE user_profile 
            SET xp_total = xp_total - %s 
            WHERE user_id = %s
        """, (xp_amount, user_id))
        
        # Register the removal in xp_history
        cursor.execute("""
            INSERT INTO xp_history (user_id, xp_change, change_reason, change_timestamp) 
            VALUES (%s, %s, %s, %s)
        """, (user_id, -xp_amount, reason, datetime.now()))

        db.commit()
        print(f"\033[32mXP removed: {xp_amount} XP from user {user_id}. Reason: {reason}.\033[0m")

    except mysql.connector.Error as err:
        db.rollback()
        print(f"\033[31mError removing XP: {err}\033[0m")


def check_level_up(user_id, cursor, db):
    # Get the user's total XP
    cursor.execute("SELECT xp_total, level FROM user_profile WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()
    
    if not user_data:
        print(f"\033[31mUser {user_id} not found.\033[0m")
        return False

    xp_total, current_level = user_data

    # Check the level that corresponds to the total XP
    cursor.execute("""
        SELECT level, xp_required, reward_description 
        FROM user_levels 
        WHERE xp_required <= %s
        ORDER BY level DESC LIMIT 1
    """, (xp_total,))
    
    new_level_data = cursor.fetchone()
    
    if new_level_data and new_level_data[0] > current_level:
        new_level, xp_required, reward = new_level_data
        
        # Update user level if they have leveled up
        cursor.execute("""
            UPDATE user_profile 
            SET level = %s 
            WHERE user_id = %s
        """, (new_level, user_id))
        db.commit()
        
        print(f"User {user_id} leveled up to {new_level}! Reward: {reward}")
        return True

    elif new_level_data and new_level_data[0] < current_level:
        # In case the user has lost XP and is at a lower level
        cursor.execute("""
            UPDATE user_profile 
            SET level = %s 
            WHERE user_id = %s
        """, (new_level_data[0], user_id))
        db.commit()
        print(f"User {user_id} has been demoted to level {new_level_data[0]}.")

    return False

