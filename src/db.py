import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_conn():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        auth_plugin='mysql_native_password',
        ssl_disabled=True
    )
    return conn
