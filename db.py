import os
import psycopg2
from dotenv import load_dotenv

# ensure environment variables are loaded once when module is imported
load_dotenv()


def get_db_connection():
    """Devuelve una conexión a la base de datos usando variables de entorno."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
