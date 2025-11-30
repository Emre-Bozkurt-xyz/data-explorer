from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Postgres URL for local dev (we’ll later run Postgres via Docker)
    database_url: str = (
        "postgresql+psycopg://dataexplorer:dataexplorer@localhost:5432/dataexplorer"
    )

    # later: add other settings (API prefix, env, etc.)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DE_",  # e.g. DE_DATABASE_URL overrides default
    )


settings = Settings()
