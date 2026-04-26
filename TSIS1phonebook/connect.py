import psycopg2
from config import get_db_config

def get_connection():
    config = get_db_config()
    return psycopg2.connect(**config)