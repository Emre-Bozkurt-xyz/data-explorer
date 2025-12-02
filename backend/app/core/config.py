# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # This is the DB URL used by default (e.g. in Docker)
    database_url: str = "postgresql+psycopg://dataexplorer:dataexplorer@db:5432/dataexplorer"

    model_config = SettingsConfigDict(
        env_file=".env",
        # no prefix => env var is just DATABASE_URL
        env_prefix="",
    )


settings = Settings()
