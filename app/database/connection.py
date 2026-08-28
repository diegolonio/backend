import psycopg
from psycopg.rows import dict_row
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2]/".env",
        extra="ignore"
    )
    database_url: str

settings = Settings()

def get_connection():
    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        yield conn


