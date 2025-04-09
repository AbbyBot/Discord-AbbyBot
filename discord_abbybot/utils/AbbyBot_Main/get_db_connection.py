import mysql.connector
from dotenv import load_dotenv
import os

# Load dotenv variables
load_dotenv()

# MySQL connection setup
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# Establish MySQL connection
def get_db_connection():
    return mysql.connector.connect(**db_config)
