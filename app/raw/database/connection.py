import psycopg
from psycopg.rows import dict_row

from app.database.config import settings

def get_connection():
    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        yield conn
