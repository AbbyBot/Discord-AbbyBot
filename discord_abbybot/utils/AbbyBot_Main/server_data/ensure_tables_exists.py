# Ensure necessary tables exist in the database
def ensure_tables_exist(cursor):
    tables = ['server_settings', 'dashboard', 'user_profile', 'mention_counter']
    for table in tables:
        cursor.execute(f"SHOW TABLES LIKE '{table}';")
        if cursor.fetchone() is None:
            print("\033[31m" + f"Table {table} does not exist. You should create it." + "\033[0m")
        else:
            print("\033[32m" + f"Table {table} already exists." + "\033[0m")