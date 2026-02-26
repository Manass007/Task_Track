import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME", "cms_db"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "Hype1204@"),
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     os.getenv("DB_PORT", "5432"),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)